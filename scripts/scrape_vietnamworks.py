"""
scrape_vietnamworks.py — Thu thập tin tuyển dụng IT từ VietnamWorks.

VietnamWorks expose một search API JSON công khai (dùng cho chính trang web của
họ), nên ta gọi thẳng API thay vì parse HTML — ổn định và đúng tinh thần "API"
của đề bài.

    POST https://ms.vietnamworks.com/job-search/v1.0/search
    body: {"userId":0,"query":"<keyword>","filter":[...],"ranges":[],
           "order":[],"hitsPerPage":50,"page":<n>,"retrieveFields":[...]}

⚠️ GIỚI HẠN MÔI TRƯỜNG: trong môi trường CI nội bộ, mọi host KHÁC GitHub
đều bị chặn egress (403) nên script này KHÔNG chạy được ở đây. Nó chạy bình
thường trên máy cá nhân hoặc runner có internet mở. KHÔNG bịa dữ liệu khi bị chặn.

Cách dùng:
    python scripts/scrape_vietnamworks.py --pages 20 --query "developer"
    python scripts/scrape_vietnamworks.py --pages 40            # nhiều keyword IT

Đầu ra: cùng schema với ItViec (job_title, company, location, salary, skills...)
gộp vào data/vietnamworks_jobs.csv qua csv_writer (idempotent).
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import HTTP_HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT, DATA_DIR
from csv_writer import upsert_rows

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

API_URL = "https://ms.vietnamworks.com/job-search/v1.0/search"
CSV_PATH = DATA_DIR / "vietnamworks_jobs.csv"

# Các từ khóa IT để quét rộng (mỗi keyword ~ vài trăm tin).
DEFAULT_QUERIES = [
    "developer", "software engineer", "data", "devops", "tester qa",
    "business analyst", "mobile", "frontend", "backend", "fullstack",
]

RETRIEVE_FIELDS = [
    "address", "benefits", "jobTitle", "salaryMin", "salaryMax",
    "isSalaryVisible", "companyName", "skills", "jobUrl", "prettySalary",
    "workingLocations", "jobFunction",
]


def today_vn() -> date:
    return (datetime.now(timezone.utc) + timedelta(hours=7)).date()


def _post(query: str, page: int) -> dict:
    """Gọi 1 trang search API. Trả về JSON (hoặc {} nếu lỗi)."""
    payload = {
        "userId": 0, "query": query, "filter": [], "ranges": [], "order": [],
        "hitsPerPage": 50, "page": page, "retrieveFields": RETRIEVE_FIELDS,
        "summaryVrnViewedJob": False,
    }
    headers = {**HTTP_HEADERS, "Content-Type": "application/json",
               "Accept": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as err:
        log.error("[vnw] %s p%d lỗi: %s", query, page, err)
        return {}


def _parse_hit(hit: Dict, target_date: date) -> Dict:
    """Map 1 job VietnamWorks -> schema chuẩn (giống ItViec)."""
    skills = hit.get("skills") or []
    skill_names = ";".join(sorted({
        (s.get("skillName") if isinstance(s, dict) else str(s)) for s in skills
    } - {None, ""}))
    locs = hit.get("workingLocations") or []
    location = ";".join(sorted({
        (l.get("cityName") if isinstance(l, dict) else str(l)) for l in locs
    } - {None, ""})) or (hit.get("address") or "")
    smin, smax = hit.get("salaryMin"), hit.get("salaryMax")
    visible = hit.get("isSalaryVisible", True)
    return {
        "scrape_date": target_date.isoformat(),
        "source_url": hit.get("jobUrl") or "",
        "job_title": hit.get("jobTitle") or "",
        "company": hit.get("companyName") or "",
        "location": location,
        "salary": hit.get("prettySalary") or "",
        "salary_min_usd": smin if smin else None,
        "salary_max_usd": smax if smax else None,
        "salary_currency": "USD" if (smin or smax) else "",
        "salary_status": "visible" if visible and (smin or smax) else "negotiable",
        "skills": skill_names,
        "source": "VietnamWorks",
        "status": "ok" if hit.get("jobUrl") else "pending",
    }


def scrape(queries: List[str], pages: int, target_date: date) -> List[Dict]:
    jobs: List[Dict] = []
    seen = set()
    for q in queries:
        for page in range(0, pages):
            data = _post(q, page)
            hits = (data.get("data") or data.get("hits") or [])
            if not hits:
                break
            for hit in hits:
                job = _parse_hit(hit, target_date)
                key = job["source_url"]
                if key and key not in seen:
                    seen.add(key)
                    jobs.append(job)
            log.info("[vnw] '%s' trang %d: +%d (tổng unique %d)", q, page, len(hits), len(jobs))
            time.sleep(REQUEST_DELAY)
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser(description="VietnamWorks IT job collector (API)")
    ap.add_argument("--pages", type=int, default=20, help="Số trang/keyword (50 job/trang)")
    ap.add_argument("--query", action="append", help="Keyword (lặp được). Mặc định: bộ IT.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    queries = args.query or DEFAULT_QUERIES
    rows = scrape(queries, args.pages, today_vn())
    if not rows:
        log.error("Không thu được job (có thể bị chặn egress hoặc API đổi schema). "
                  "Chạy trên máy có internet mở. KHÔNG ghi dữ liệu giả.")
        return 2
    if args.dry_run:
        log.info("[DRY-RUN] thu %d job, không ghi.", len(rows))
    else:
        res = upsert_rows(CSV_PATH, rows)
        log.info("CSV: inserted=%d updated=%d total=%d", res["inserted"],
                 res["updated"], res["total_rows"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
