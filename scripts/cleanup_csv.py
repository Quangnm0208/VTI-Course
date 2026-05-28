"""
cleanup_csv.py — Dọn dẹp CSV định kỳ.

Tác vụ:
    - Loại bỏ dòng trùng lặp theo khóa upsert (scrape_date, source_url)
    - Loại bỏ dòng "pending" cũ quá N ngày (đã được job 'ok' khác thay thế)
    - In thống kê tóm tắt

Run:
    python scripts/cleanup_csv.py            # dry-run (chỉ in ra)
    python scripts/cleanup_csv.py --apply    # áp dụng thay đổi
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CSV_PATH
from csv_writer import _atomic_write, deduplicate, read_csv

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def cleanup_old_pending(csv_path: Path, keep_days: int = 7, apply: bool = False) -> int:
    """
    Loại bỏ các dòng status='pending' có scrape_date cũ hơn `keep_days`.
    Trả về số dòng đã (sẽ) bị xóa.
    """
    rows = read_csv(csv_path)
    if not rows:
        return 0

    cutoff = (date.today() - timedelta(days=keep_days)).isoformat()
    kept, removed = [], 0
    for r in rows:
        if r.get("status") == "pending" and r.get("scrape_date", "") < cutoff:
            removed += 1
        else:
            kept.append(r)

    if apply and removed > 0:
        _atomic_write(csv_path, kept)

    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup CSV ItViec")
    parser.add_argument("--csv", default=str(CSV_PATH))
    parser.add_argument("--apply", action="store_true",
                        help="Áp dụng thay đổi (mặc định: dry-run)")
    parser.add_argument("--keep-pending-days", type=int, default=7,
                        help="Số ngày tối đa giữ dòng pending")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        log.info("CSV chưa tồn tại: %s -> bỏ qua cleanup.", csv_path)
        return 0

    rows_before = read_csv(csv_path)
    log.info("Trước cleanup: %d dòng", len(rows_before))

    # Bước 1: dedupe
    if args.apply:
        n_dup = deduplicate(csv_path)
    else:
        # Đếm thử bằng cách build dict
        seen = {}
        for r in rows_before:
            seen[(r.get("scrape_date", ""), r.get("source_url", ""))] = r
        n_dup = len(rows_before) - len(seen)

    log.info("Trùng lặp (theo khóa upsert): %d", n_dup)

    # Bước 2: loại pending cũ
    n_old = cleanup_old_pending(csv_path, keep_days=args.keep_pending_days,
                                apply=args.apply)
    log.info("Pending cũ hơn %d ngày: %d", args.keep_pending_days, n_old)

    rows_after = read_csv(csv_path)
    log.info("Sau cleanup: %d dòng (%s)",
             len(rows_after), "ĐÃ ÁP DỤNG" if args.apply else "DRY-RUN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
