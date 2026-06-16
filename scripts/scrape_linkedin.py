"""
scrape_linkedin.py — Thu thập tin tuyển dụng IT công khai từ LinkedIn.

Dùng endpoint "jobs-guest" CÔNG KHAI của LinkedIn (không cần đăng nhập), chính
là API mà trang kết quả tìm việc gọi để tải thêm thẻ job:

    GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
        ?keywords=<kw>&location=<loc>&start=<n>      (n tăng theo bước 10)

Trả về một đoạn HTML gồm các <li> thẻ job -> parse bằng BeautifulSoup.

⚠️ LƯU Ý QUAN TRỌNG:
  - Chỉ dùng endpoint CÔNG KHAI, KHÔNG đăng nhập, KHÔNG vượt tường đăng nhập.
  - Tôn trọng Điều khoản dịch vụ & robots của LinkedIn; chỉ phục vụ mục đích
    học tập, thu thập lượng nhỏ với delay lịch sự. Không dùng cho mục đích thương mại.
  - GIỚI HẠN MÔI TRƯỜNG: sandbox nội bộ chặn mọi host khác GitHub (403) nên
    script KHÔNG chạy được ở đây; chạy trên máy cá nhân/CI có internet mở.
  - KHÔNG bịa dữ liệu khi bị chặn.

Cách dùng:
    python scripts/scrape_linkedin.py --keywords "software developer" \
        --location "Vietnam" --pages 40
Đầu ra: data/linkedin_jobs.csv (schema chuẩn, gộp idempotent qua csv_writer).
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import HTTP_HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT, DATA_DIR
from csv_writer import upsert_rows

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

GUEST_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
CSV_PATH = DATA_DIR / "linkedin_jobs.csv"

# Bộ keyword IT mặc định để quét rộng tại thị trường Việt Nam.
DEFAULT_KEYWORDS = [
    "software developer", "data analyst", "data engineer", "devops",
    "backend developer", "frontend developer", "qa engineer",
]


def today_vn() -> date:
    return (datetime.now(timezone.utc) + timedelta(hours=7)).date()


def _fetch(keywords: str, location: str, start: int) -> str | None:
    qs = urlencode({"keywords": keywords, "location": location, "start": start})
    url = f"{GUEST_API}?{qs}"
    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code == 429:
            log.warning("[li] 429 rate limited -> nghỉ 30s"); time.sleep(30); return None
        r.raise_for_status()
        return r.text
    except requests.RequestException as err:
        log.error("[li] %s start=%d lỗi: %s", keywords, start, err)
        return None


def _parse_cards(html: str, keywords: str, target_date: date) -> List[Dict]:
    """Parse đoạn HTML job-cards -> list job dict schema chuẩn."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for li in soup.find_all("li"):
        title_tag = li.find(class_=lambda c: c and "title" in c)
        if not title_tag:
            continue
        company_tag = li.find(class_=lambda c: c and "subtitle" in c)
        loc_tag = li.find(class_=lambda c: c and "location" in c)
        link_tag = li.find("a", href=True)
        url = (link_tag["href"].split("?")[0] if link_tag else "")
        out.append({
            "scrape_date": target_date.isoformat(),
            "source_url": url,
            "job_title": title_tag.get_text(strip=True),
            "company": company_tag.get_text(strip=True) if company_tag else "",
            "location": loc_tag.get_text(strip=True) if loc_tag else "",
            "salary": "",                       # endpoint công khai không kèm lương
            "salary_min_usd": None, "salary_max_usd": None,
            "salary_currency": "", "salary_status": "none",
            "skills": "",                       # cần fetch trang chi tiết mới có
            "source": "LinkedIn",
            "status": "ok" if url else "pending",
        })
    return out


def scrape(keywords_list: List[str], location: str, pages: int,
           target_date: date) -> List[Dict]:
    jobs, seen = [], set()
    for kw in keywords_list:
        for page in range(pages):
            html = _fetch(kw, location, page * 10)
            if not html:
                break
            cards = _parse_cards(html, kw, target_date)
            if not cards:
                break
            for job in cards:
                if job["source_url"] and job["source_url"] not in seen:
                    seen.add(job["source_url"]); jobs.append(job)
            log.info("[li] '%s' start=%d: +%d (unique %d)", kw, page * 10, len(cards), len(jobs))
            time.sleep(REQUEST_DELAY)
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser(description="LinkedIn public job collector")
    ap.add_argument("--keywords", action="append", help="Keyword (lặp được).")
    ap.add_argument("--location", default="Vietnam")
    ap.add_argument("--pages", type=int, default=40, help="Số trang/keyword (10 job/trang)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    kws = args.keywords or DEFAULT_KEYWORDS
    rows = scrape(kws, args.location, args.pages, today_vn())
    if not rows:
        log.error("Không thu được job (bị chặn egress hoặc LinkedIn đổi markup). "
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
