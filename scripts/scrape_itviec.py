"""
scrape_itviec.py — Trình scrape tin tuyển dụng IT từ ItViec, chạy hàng ngày.

Cách dùng:
    python scripts/scrape_itviec.py                 # mặc định, dùng CSV_PATH
    python scripts/scrape_itviec.py --pages 10      # chỉ cào 10 trang
    python scripts/scrape_itviec.py --dry-run       # không ghi file
    python scripts/scrape_itviec.py --date 2026-05-28

Exit code:
    0  -> Thu được >= QUALITY_THRESHOLDS['min_jobs_per_run']
    1  -> Cảnh báo: thu được ít hơn ngưỡng (workflow vẫn pass nhờ continue-on-error)
    2  -> Lỗi nghiêm trọng (không scrape được gì)
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Cho phép import các module trong cùng folder khi chạy từ bất kỳ đâu
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    CSV_PATH, HTTP_HEADERS, ITVIEC_BASE, ITVIEC_JOBS,
    MAX_PAGES_DEFAULT, QUALITY_THRESHOLDS, REQUEST_DELAY, REQUEST_TIMEOUT,
)
from csv_writer import upsert_rows

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Hàm phụ trợ: ngày VN, salary parser, ...
# -----------------------------------------------------------------------------
def today_vn() -> date:
    """Trả về ngày hiện tại theo timezone Asia/Ho_Chi_Minh (UTC+7)."""
    return (datetime.now(timezone.utc) + timedelta(hours=7)).date()


def parse_salary(raw: str) -> tuple[Optional[float], Optional[float]]:
    """
    Tách salary text -> (min_usd, max_usd).
    Vd: "1,500 - 2,500 USD" -> (1500.0, 2500.0)
         "Negotiable"        -> (None, None)
    """
    if not raw:
        return (None, None)
    clean = raw.replace(",", "")
    # Regex tìm 2 số nối bằng "-"
    m = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", clean)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    # Chỉ có 1 con số -> coi là both min & max
    m = re.search(r"(\d+(?:\.\d+)?)", clean)
    if m:
        v = float(m.group(1))
        return (v, v)
    return (None, None)


# -----------------------------------------------------------------------------
# HTTP fetch
# -----------------------------------------------------------------------------
def fetch_page(url: str) -> Optional[str]:
    """GET 1 URL, trả về HTML hoặc None nếu lỗi."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as err:
        log.error("Lỗi tải %s: %s", url, err)
        return None


# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------
def parse_job_card(card) -> Optional[Dict]:
    """
    Bóc 1 job từ HTML card. Trả về None nếu không có title (loại card rác).
    Lưu ý: ItViec đôi khi đổi class -> ta dùng nhiều selector dự phòng (regex).
    """
    title_tag = card.find(["h3", "h2"])
    title = title_tag.get_text(strip=True) if title_tag else ""
    if not title:
        return None

    # Công ty - thử nhiều selector vì ItViec hay đổi cấu trúc HTML
    company_tag = (
        card.find("a", class_=re.compile("company"))
        or card.find("span", class_=re.compile("company"))
        or card.find(class_=re.compile("employer"))
    )
    company = company_tag.get_text(strip=True) if company_tag else ""

    # Địa điểm
    loc_tag = card.find(class_=re.compile(r"(address|location|city)"))
    location = loc_tag.get_text(strip=True) if loc_tag else ""

    # Lương (ItViec hay để "Sign in to view")
    salary_tag = card.find(class_=re.compile("salary"))
    salary_raw = salary_tag.get_text(strip=True) if salary_tag else "Negotiable"
    salary_min, salary_max = parse_salary(salary_raw)

    # Tags kỹ năng
    tag_nodes = card.find_all(class_=re.compile(r"(itag|tag|skill)"))
    tags = [t.get_text(strip=True) for t in tag_nodes if t.get_text(strip=True)]
    skills = ";".join(sorted({t for t in tags if t})) if tags else ""

    # Link chi tiết job (làm khóa upsert). Ưu tiên link KHÔNG trỏ tới trang
    # company - ItViec đặt link công ty ngay đầu card nên phải lọc.
    detail_url = ""
    for a in card.find_all("a", href=True):
        href = a["href"]
        if "/companies/" in href or "/employers/" in href:
            continue            # bỏ qua link company
        detail_url = href if href.startswith("http") else ITVIEC_BASE + href
        break
    if not detail_url:
        # Fallback: lấy link đầu tiên nếu không có link nào khác
        first = card.find("a", href=True)
        if first:
            href = first["href"]
            detail_url = href if href.startswith("http") else ITVIEC_BASE + href

    return {
        "job_title":      title,
        "company":        company,
        "location":       location,
        "salary":         salary_raw,
        "salary_min_usd": salary_min,
        "salary_max_usd": salary_max,
        "skills":         skills,
        "source_url":     detail_url,
        "source":         "ItViec",
        "status":         "ok" if detail_url else "pending",
    }


def scrape_itviec(target_date: date, max_pages: int) -> List[Dict]:
    """
    Lặp qua các trang ItViec và bóc danh sách job.
    Trả về list các dict đã gắn scrape_date.
    """
    log.info("═══ ItViec scrape — %s (tối đa %d trang) ═══", target_date, max_pages)

    all_jobs: List[Dict] = []

    for page in range(1, max_pages + 1):
        url = f"{ITVIEC_JOBS}?page={page}"
        html = fetch_page(url)
        if not html:
            log.warning("Trang %d lỗi, bỏ qua.", page)
            continue

        soup = BeautifulSoup(html, "html.parser")

        # Tìm card theo nhiều layout khác nhau
        cards = (
            soup.find_all("div", class_=re.compile(r"job.?card|ipy-3"))
            or soup.find_all("section", class_=re.compile("job"))
            or soup.find_all("article")
        )

        if not cards:
            log.info("Trang %d không có job card -> dừng.", page)
            break

        page_jobs = 0
        for card in cards:
            try:
                job = parse_job_card(card)
                if not job:
                    continue
                job["scrape_date"] = target_date.isoformat()
                all_jobs.append(job)
                page_jobs += 1
            except Exception as err:
                log.warning("Lỗi parse card: %s", err)

        log.info("Trang %2d: thu %d job", page, page_jobs)

        # Nghỉ giữa các trang
        time.sleep(REQUEST_DELAY)

    log.info("─" * 60)
    log.info("Tổng cộng: %d job", len(all_jobs))
    return all_jobs


# -----------------------------------------------------------------------------
# Hàm chính
# -----------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="ItViec daily scraper")
    parser.add_argument("--csv", default=str(CSV_PATH), help="Đường dẫn CSV đầu ra")
    parser.add_argument("--pages", type=int, default=MAX_PAGES_DEFAULT,
                        help="Số trang tối đa cần cào")
    parser.add_argument("--date", help="Ngày scrape YYYY-MM-DD (mặc định: hôm nay VN)")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi CSV")
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else today_vn()

    rows = scrape_itviec(target_date, max_pages=args.pages)

    if not rows:
        log.error("KHÔNG thu được job nào - thoát với exit code 2")
        return 2

    if args.dry_run:
        log.info("[DRY-RUN] Không ghi CSV.")
    else:
        result = upsert_rows(args.csv, rows)
        log.info(
            "CSV upsert: inserted=%d, updated=%d, total=%d",
            result["inserted"], result["updated"], result["total_rows"],
        )

    # Cảnh báo nếu thu ít hơn ngưỡng (không fail hard)
    min_threshold = QUALITY_THRESHOLDS["min_jobs_per_run"]
    if len(rows) < min_threshold:
        log.warning(
            "Chỉ thu %d/%d job (< ngưỡng tối thiểu) - exit 1",
            len(rows), min_threshold,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
