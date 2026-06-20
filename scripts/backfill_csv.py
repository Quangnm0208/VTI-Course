"""
backfill_csv.py — Vá dữ liệu ItViec ĐÃ thu thập trước đây.

Vì sao cần: các lần scrape cũ lưu nhầm link '/sign_in?job=...' vào source_url
và bỏ trống company/salary_status. Script này sửa tại chỗ (idempotent):

  1. source_url '/sign_in?job=<slug>' -> canonical 'https://itviec.com/it/<slug>'
  2. company trống -> derive từ slug job
  3. salary 'Sign in to view salary'  -> salary_status='login_required'
     (không ước đoán lương; chỉ ghi đúng trạng thái)
  4. điền salary_currency / salary_status cho mọi dòng dựa trên text salary

Cách dùng:
    python scripts/backfill_csv.py            # ghi đè data/itviec_jobs.csv
    python scripts/backfill_csv.py --dry-run  # chỉ in thống kê, không ghi
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CSV_PATH
from csv_writer import read_csv, _atomic_write
from scrape_itviec import (
    canonical_job_url, company_from_slug, detect_currency,
    salary_status_from_text,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def backfill(rows: list[dict]) -> dict:
    stats = {"url_fixed": 0, "company_filled": 0, "status_set": 0}
    for r in rows:
        url = r.get("source_url", "")
        if "sign_in" in url:
            new_url = canonical_job_url(url)
            if new_url != url:
                r["source_url"] = new_url
                stats["url_fixed"] += 1
                url = new_url

        if not r.get("company") and url:
            slug = url.rstrip("/").split("/")[-1]
            comp = company_from_slug(slug)
            if comp:
                r["company"] = comp
                stats["company_filled"] += 1

        sal_text = r.get("salary", "")
        if not r.get("salary_status"):
            r["salary_status"] = salary_status_from_text(sal_text)
            stats["status_set"] += 1
        if not r.get("salary_currency"):
            r["salary_currency"] = detect_currency(sal_text)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill/repair ItViec CSV cũ")
    ap.add_argument("--csv", default=str(CSV_PATH))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_csv(args.csv)
    if not rows:
        log.error("Không đọc được dòng nào từ %s", args.csv)
        return 1

    stats = backfill(rows)
    log.info("Backfill %d dòng: %s", len(rows), stats)

    if args.dry_run:
        log.info("[DRY-RUN] Không ghi file.")
    else:
        _atomic_write(Path(args.csv), rows)
        log.info("Đã ghi đè %s", args.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
