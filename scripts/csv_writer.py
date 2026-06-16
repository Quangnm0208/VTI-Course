"""
csv_writer.py — Idempotent UPSERT vào CSV với atomic write.

- Khóa idempotent: (scrape_date, source_url)
- Cùng khóa đã tồn tại  -> UPDATE (ghi đè)
- Khóa mới                -> INSERT
- Ghi file an toàn: tmp -> fsync -> rename (tránh corrupt khi process bị kill)
"""

from __future__ import annotations

import csv
import logging
import os
import tempfile
from pathlib import Path

from config import CSV_COLUMNS, UPSERT_KEY

log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Đọc CSV hiện có
# -----------------------------------------------------------------------------
def read_csv(csv_path: str | Path) -> list[dict]:
    """Đọc CSV và trả về list các dict. Trả về [] nếu file chưa tồn tại."""
    path = Path(csv_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# -----------------------------------------------------------------------------
# UPSERT chính
# -----------------------------------------------------------------------------
def upsert_rows(csv_path: str | Path, new_rows: list[dict]) -> dict:
    """
    UPSERT idempotent:
        1. Đọc CSV hiện có vào memory
        2. Với mỗi dòng mới:
            - Tính key = (scrape_date, source_url)
            - Nếu key đã tồn tại -> UPDATE
            - Nếu chưa            -> INSERT
        3. Ghi atomic ra đĩa

    Returns:
        Dict thống kê: {'inserted': N, 'updated': N, 'total_rows': N}
    """
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    existing = read_csv(csv_path)

    # Index dữ liệu cũ theo khóa upsert để tra O(1)
    by_key: dict[tuple, dict] = {}
    for row in existing:
        k = tuple(row.get(c, "") for c in UPSERT_KEY)
        by_key[k] = row

    inserted = 0
    updated = 0

    for new_row in new_rows:
        # Chuẩn hóa: chỉ giữ các cột trong schema, ép về string
        normalized = {c: _normalize(new_row.get(c)) for c in CSV_COLUMNS}
        k = tuple(normalized[c] for c in UPSERT_KEY)

        if not k[1]:
            # Bỏ qua dòng không có source_url (không xác định được key)
            log.warning("Bỏ qua dòng không có source_url: %s", normalized.get("job_title"))
            continue

        if k in by_key:
            # UPDATE: ghi đè giá trị mới lên dòng cũ
            by_key[k].update(normalized)
            updated += 1
        else:
            # INSERT
            existing.append(normalized)
            by_key[k] = normalized
            inserted += 1

    # Sort ổn định: scrape_date giảm dần, sau đó company, job_title
    existing.sort(
        key=lambda r: (
            r.get("scrape_date", ""),
            r.get("company", ""),
            r.get("job_title", ""),
        ),
        reverse=False,
    )

    _atomic_write(csv_path, existing)

    return {
        "inserted":   inserted,
        "updated":    updated,
        "total_rows": len(existing),
    }


# -----------------------------------------------------------------------------
# Atomic write
# -----------------------------------------------------------------------------
def _atomic_write(csv_path: Path, rows: list[dict]) -> None:
    """Ghi CSV theo pattern atomic: tmp file -> fsync -> rename."""
    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix=".tmp_", suffix=".csv", dir=csv_path.parent,
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            f.flush()
            os.fsync(f.fileno())
        # os.replace là atomic trên cùng filesystem
        os.replace(tmp_path, csv_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _normalize(value) -> str:
    """Convert giá trị thành chuỗi an toàn cho CSV."""
    if value is None:
        return ""
    if isinstance(value, float):
        # Tránh ký hiệu khoa học và số 0 thừa
        if value == int(value):
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value).strip()


# -----------------------------------------------------------------------------
# Cleanup helper
# -----------------------------------------------------------------------------
def deduplicate(csv_path: str | Path) -> int:
    """
    Loại bản ghi trùng lặp theo khóa upsert (chỉ giữ bản ghi mới nhất theo
    thứ tự xuất hiện cuối cùng trong file). Trả về số dòng đã xóa.
    """
    rows = read_csv(csv_path)
    if not rows:
        return 0

    seen: dict[tuple, dict] = {}
    for r in rows:
        k = tuple(r.get(c, "") for c in UPSERT_KEY)
        seen[k] = r           # Giá trị sau ghi đè giá trị trước

    deduped = list(seen.values())
    removed = len(rows) - len(deduped)
    if removed > 0:
        deduped.sort(
            key=lambda r: (
                r.get("scrape_date", ""),
                r.get("company", ""),
                r.get("job_title", ""),
            )
        )
        _atomic_write(Path(csv_path), deduped)
        log.info("Cleanup: loại %d dòng trùng lặp", removed)
    return removed
