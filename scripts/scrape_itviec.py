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
from fetcher import PlaywrightFetcher, fetch_with_requests

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
# HTTP fetch wrapper (legacy - giữ để backward compatible với test cũ)
# -----------------------------------------------------------------------------
def fetch_page(url: str) -> Optional[str]:
    """Wrapper gọi engine 'requests' để giữ tương thích."""
    return fetch_with_requests(url)


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

    # Công ty - ItViec hay đặt tên công ty bên trong link "/companies/SLUG"
    # nên ta tìm tag <a> trỏ tới /companies/ trước, sau đó fallback các class.
    company = ""
    company_link = card.find("a", href=re.compile(r"/companies/"))
    if company_link:
        company = company_link.get_text(strip=True)
    if not company:
        company_tag = (
            card.find("a", class_=re.compile("company"))
            or card.find("span", class_=re.compile("company"))
            or card.find(class_=re.compile("employer"))
        )
        if company_tag:
            company = company_tag.get_text(strip=True)
    if not company:
        # Phương án cuối: lấy slug từ URL /companies/SLUG -> derive tên
        if company_link and company_link.get("href"):
            slug = company_link["href"].rstrip("/").split("/")[-1]
            company = slug.replace("-", " ").title()

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


def parse_job_detail(html: str) -> Dict:
    """
    Parse trang CHI TIẾT job để bóc salary + mô tả + thông tin sâu hơn.

    ItViec thường nhúng salary trong JSON-LD (script type=application/ld+json)
    theo schema.org/JobPosting → đó là nguồn tin cậy nhất, kể cả khi UI ẩn
    behind login wall.
    """
    soup = BeautifulSoup(html, "html.parser")
    result = {"salary_min_usd": None, "salary_max_usd": None,
              "salary_currency": "", "salary_source": "none"}

    # 1) Ưu tiên đọc JSON-LD schema.org/JobPosting
    import json as _json
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = _json.loads(script.string or "{}")
        except (_json.JSONDecodeError, TypeError):
            continue
        # JSON-LD có thể là list hoặc dict
        items = data if isinstance(data, list) else [data]
        for item in items:
            if item.get("@type") != "JobPosting":
                continue
            base = item.get("baseSalary") or {}
            value = base.get("value") or {}
            cur = base.get("currency", "")
            if isinstance(value, dict):
                lo, hi = value.get("minValue"), value.get("maxValue")
                if lo or hi:
                    result["salary_min_usd"] = lo
                    result["salary_max_usd"] = hi
                    result["salary_currency"] = cur
                    result["salary_source"] = "json-ld"
                    return result
            elif value:
                result["salary_min_usd"] = value
                result["salary_max_usd"] = value
                result["salary_currency"] = cur
                result["salary_source"] = "json-ld"
                return result

    # 2) Fallback: tìm text salary trong DOM
    salary_node = soup.find(class_=re.compile(r"salary", re.I))
    if salary_node:
        txt = salary_node.get_text(strip=True)
        if "sign in" not in txt.lower() and txt:
            lo, hi = parse_salary(txt)
            if lo or hi:
                result["salary_min_usd"] = lo
                result["salary_max_usd"] = hi
                result["salary_currency"] = "USD"
                result["salary_source"] = "dom-text"
    return result


def enrich_with_details(jobs: List[Dict], fetcher, max_jobs: int = 100) -> List[Dict]:
    """
    Cào trang chi tiết để bổ sung salary thật cho từng job.

    Args:
        jobs:     list job dict từ scrape_itviec()
        fetcher:  PlaywrightFetcher context (đã start) hoặc callable requests
        max_jobs: giới hạn để không chạy quá lâu (mặc định 100 job)

    Returns: list jobs đã được update salary_min_usd / salary_max_usd.
    """
    log.info("=== Enrich %d job đầu tiên với chi tiết salary ===",
             min(len(jobs), max_jobs))

    enriched = 0
    for i, job in enumerate(jobs[:max_jobs]):
        url = job.get("source_url", "")
        if not url:
            continue

        # Hỗ trợ cả callable (requests) và PlaywrightFetcher
        if callable(fetcher):
            html = fetcher(url)
        else:
            html = fetcher.fetch(url)
        if not html:
            continue

        detail = parse_job_detail(html)
        if detail.get("salary_min_usd") or detail.get("salary_max_usd"):
            job["salary_min_usd"] = detail["salary_min_usd"]
            job["salary_max_usd"] = detail["salary_max_usd"]
            job["salary"] = (
                f"{detail['salary_min_usd']}-{detail['salary_max_usd']} "
                f"{detail['salary_currency']}".strip()
            )
            enriched += 1

        if (i + 1) % 10 == 0:
            log.info("  Đã enrich %d/%d (thành công: %d)", i + 1, len(jobs), enriched)
        time.sleep(REQUEST_DELAY)

    log.info("Enrich xong: %d/%d job có salary thật", enriched, min(len(jobs), max_jobs))
    return jobs


def _parse_page(html: str) -> List[Dict]:
    """Parse 1 trang HTML, trả về list job dict (chưa gắn scrape_date)."""
    soup = BeautifulSoup(html, "html.parser")
    cards = (
        soup.find_all("div", class_=re.compile(r"job.?card|ipy-3"))
        or soup.find_all("section", class_=re.compile("job"))
        or soup.find_all("article")
    )
    jobs = []
    for card in cards:
        try:
            job = parse_job_card(card)
            if job:
                jobs.append(job)
        except Exception as err:
            log.warning("Lỗi parse card: %s", err)
    return jobs


def scrape_itviec(
    target_date: date,
    max_pages: int,
    engine: str = "playwright",
) -> List[Dict]:
    """
    Lặp qua các trang ItViec, hỗ trợ 2 engine:
        - 'playwright' (mặc định): vượt Cloudflare, an toàn cho production.
        - 'requests':              nhanh hơn, nhưng dễ bị 403.

    Khi engine='playwright' bị fail liên tục, tự fallback sang 'requests'.
    """
    log.info("═══ ItViec scrape — %s | engine=%s | tối đa %d trang ═══",
             target_date, engine, max_pages)

    all_jobs: List[Dict] = []

    if engine == "playwright":
        # Mở 1 browser session, dùng chung cho mọi trang
        try:
            with PlaywrightFetcher() as fetcher:
                for page_num in range(1, max_pages + 1):
                    url = f"{ITVIEC_JOBS}?page={page_num}"
                    html = fetcher.fetch(url)
                    page_jobs = _parse_page(html) if html else []
                    for job in page_jobs:
                        job["scrape_date"] = target_date.isoformat()
                    all_jobs.extend(page_jobs)
                    log.info("Trang %2d: thu %d job", page_num, len(page_jobs))

                    # Nếu trang đầu đã rỗng -> dừng sớm (có thể bị block)
                    if page_num == 1 and not page_jobs:
                        log.warning("Trang 1 rỗng -> dừng, thử fallback 'requests'")
                        break
                    time.sleep(REQUEST_DELAY)
        except ImportError:
            log.error("Playwright chưa được cài. Chạy: pip install playwright "
                      "&& playwright install chromium")
            engine = "requests"     # fallback

        # Fallback nếu Playwright không thu được gì
        if not all_jobs:
            log.warning("Playwright không thu được job -> thử lại bằng requests")
            engine = "requests"

    if engine == "requests" and not all_jobs:
        for page_num in range(1, max_pages + 1):
            url = f"{ITVIEC_JOBS}?page={page_num}"
            html = fetch_with_requests(url)
            page_jobs = _parse_page(html) if html else []
            for job in page_jobs:
                job["scrape_date"] = target_date.isoformat()
            all_jobs.extend(page_jobs)
            log.info("Trang %2d: thu %d job", page_num, len(page_jobs))
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
    parser.add_argument(
        "--engine", choices=["playwright", "requests"], default="playwright",
        help="Engine fetch HTML. 'playwright' vượt Cloudflare (mặc định).",
    )
    parser.add_argument(
        "--enrich-details", type=int, default=0, metavar="N",
        help="Cào chi tiết N job đầu để lấy salary từ JSON-LD (chậm hơn ~3x).",
    )
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else today_vn()

    rows = scrape_itviec(target_date, max_pages=args.pages, engine=args.engine)

    # Enrich salary bằng cách cào trang chi tiết (tùy chọn)
    if rows and args.enrich_details > 0:
        from fetcher import PlaywrightFetcher, fetch_with_requests
        if args.engine == "playwright":
            with PlaywrightFetcher() as f:
                rows = enrich_with_details(rows, f, max_jobs=args.enrich_details)
        else:
            rows = enrich_with_details(rows, fetch_with_requests,
                                       max_jobs=args.enrich_details)

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
