"""Tests cho csv_writer.upsert_rows: kiểm tra tính idempotent của UPSERT."""

import sys
from pathlib import Path

import pytest

# Cho phép import module trong scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from csv_writer import deduplicate, read_csv, upsert_rows


def _make_row(scrape_date: str, url: str, title: str = "Dev", status: str = "ok") -> dict:
    return {
        "scrape_date":    scrape_date,
        "source_url":     url,
        "job_title":      title,
        "company":        "ACME",
        "location":       "HCM",
        "salary":         "1000-2000 USD",
        "salary_min_usd": 1000,
        "salary_max_usd": 2000,
        "skills":         "Python;SQL",
        "source":         "ItViec",
        "status":         status,
    }


def test_insert_new_rows(tmp_path: Path):
    csv = tmp_path / "data.csv"
    rows = [_make_row("2026-05-28", "https://itviec.com/job/1")]

    result = upsert_rows(csv, rows)

    assert result == {"inserted": 1, "updated": 0, "total_rows": 1}
    assert csv.exists()
    assert len(read_csv(csv)) == 1


def test_upsert_is_idempotent(tmp_path: Path):
    """Chạy upsert 2 lần với cùng data -> tổng vẫn 1 dòng (key duplicate)."""
    csv = tmp_path / "data.csv"
    rows = [_make_row("2026-05-28", "https://itviec.com/job/1")]

    upsert_rows(csv, rows)
    result = upsert_rows(csv, rows)

    assert result["inserted"] == 0
    assert result["updated"] == 1
    assert result["total_rows"] == 1


def test_update_overwrites_existing(tmp_path: Path):
    csv = tmp_path / "data.csv"
    r1 = _make_row("2026-05-28", "https://itviec.com/job/1", title="Dev v1")
    r2 = _make_row("2026-05-28", "https://itviec.com/job/1", title="Dev v2")

    upsert_rows(csv, [r1])
    upsert_rows(csv, [r2])

    rows = read_csv(csv)
    assert len(rows) == 1
    assert rows[0]["job_title"] == "Dev v2"


def test_different_date_same_url_is_separate_row(tmp_path: Path):
    """Cùng URL, khác scrape_date -> coi là 2 bản ghi khác nhau."""
    csv = tmp_path / "data.csv"
    upsert_rows(csv, [_make_row("2026-05-28", "https://itviec.com/job/1")])
    upsert_rows(csv, [_make_row("2026-05-29", "https://itviec.com/job/1")])

    assert len(read_csv(csv)) == 2


def test_skip_row_without_url(tmp_path: Path):
    csv = tmp_path / "data.csv"
    rows = [_make_row("2026-05-28", "")]   # source_url rỗng
    result = upsert_rows(csv, rows)
    assert result["inserted"] == 0
    assert result["total_rows"] == 0


def test_deduplicate(tmp_path: Path):
    """deduplicate() loại các dòng trùng key, giữ giá trị cuối."""
    csv = tmp_path / "data.csv"
    # Tạo file CSV thủ công có 2 dòng trùng key
    rows = [
        _make_row("2026-05-28", "https://itviec.com/job/1", title="v1"),
    ]
    upsert_rows(csv, rows)

    # Append thêm bằng ghi trực tiếp (giả lập trùng)
    import csv as csv_mod
    from config import CSV_COLUMNS

    with csv.open("a", encoding="utf-8", newline="") as f:
        w = csv_mod.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        w.writerow(_make_row("2026-05-28", "https://itviec.com/job/1", title="v2"))

    assert len(read_csv(csv)) == 2     # Trước cleanup
    removed = deduplicate(csv)
    assert removed == 1
    assert len(read_csv(csv)) == 1
