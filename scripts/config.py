"""
config.py — Cấu hình tập trung cho pipeline scraping ItViec.

Quy ước CSV và idempotency key dùng chung cho toàn bộ scripts.
"""

from __future__ import annotations
import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Đường dẫn
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
CSV_PATH     = DATA_DIR / "itviec_jobs.csv"

# -----------------------------------------------------------------------------
# Cấu hình ItViec
# -----------------------------------------------------------------------------
ITVIEC_BASE = "https://itviec.com"
ITVIEC_JOBS = "https://itviec.com/it-jobs"
# Mẫu URL trang chi tiết job (canonical). ItViec dùng dạng /it/<slug>.
ITVIEC_JOB_DETAIL = "https://itviec.com/it/{slug}"

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    # Header gần với trình duyệt thật để giảm khả năng bị Cloudflare chặn (403).
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "vi,en;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
}

# -----------------------------------------------------------------------------
# Xác thực (để MỞ KHÓA mức lương bị ẩn sau "Sign in to view salary")
# -----------------------------------------------------------------------------
# ItViec ẩn lương với khách vãng lai. Cách hợp lệ để lấy lương thật là dùng
# CHÍNH phiên đăng nhập của bạn:
#   - ITVIEC_COOKIE : chuỗi cookie copy từ trình duyệt đã đăng nhập
#                     (DevTools -> Application -> Cookies -> copy header 'Cookie').
#   - Hoặc ITVIEC_EMAIL + ITVIEC_PASSWORD : Playwright tự đăng nhập.
# Không có thông tin này, scraper vẫn chạy nhưng đánh dấu salary_status=
# 'login_required' thay vì ước đoán.
ITVIEC_COOKIE = os.environ.get("ITVIEC_COOKIE", "").strip()
ITVIEC_EMAIL = os.environ.get("ITVIEC_EMAIL", "").strip()
ITVIEC_PASSWORD = os.environ.get("ITVIEC_PASSWORD", "").strip()

# Tỷ giá quy đổi VND -> USD (lương ItViec thường niêm yết bằng VND/tháng).
# Cho phép override qua env để cập nhật khi tỷ giá đổi.
VND_PER_USD = float(os.environ.get("VND_PER_USD", "25000"))
# Lương ItViec là theo THÁNG; nhân 12 để so với lương/năm của khảo sát SO (tùy chọn).
SALARY_MONTHS_PER_YEAR = 12

# Số trang tối đa cào mỗi lần (mỗi page ~ 20 jobs).
# Trên GitHub Actions, mặc định 30 -> ~600 jobs/ngày, an toàn timeout 10 phút.
MAX_PAGES_DEFAULT = 30

# Khoảng nghỉ giữa request (giây) - tránh bị chặn IP
REQUEST_DELAY = 2.0

# Timeout cho mỗi HTTP request
REQUEST_TIMEOUT = 30

# -----------------------------------------------------------------------------
# Schema CSV - thứ tự cột cố định để git diff dễ đọc
# -----------------------------------------------------------------------------
CSV_COLUMNS = [
    "scrape_date",      # YYYY-MM-DD (giờ VN) - khóa idempotent thứ 1
    "source_url",       # URL chi tiết job (canonical) - khóa idempotent thứ 2
    "job_title",
    "company",
    "location",
    "salary",           # raw text (có thể là "Negotiable" / "Sign in to view salary")
    "salary_min_usd",
    "salary_max_usd",
    "salary_currency",  # 'USD' | 'VND' | '' - đơn vị gốc trước khi quy đổi
    "salary_status",    # 'visible' | 'login_required' | 'negotiable' | 'none'
    "skills",           # nối bằng ';'
    "source",           # nguồn dữ liệu, vd 'ItViec'
    "status",           # 'ok' | 'pending'
]

# Khóa upsert: cùng (scrape_date, source_url) -> coi là cùng 1 bản ghi
UPSERT_KEY = ("scrape_date", "source_url")

# -----------------------------------------------------------------------------
# Ngưỡng kiểm tra chất lượng dữ liệu (Data Quality)
# -----------------------------------------------------------------------------
QUALITY_THRESHOLDS = {
    # Số lượng job tối thiểu thu được trong 1 lần scrape
    "min_jobs_per_run":   50,
    # Số lượng job tối đa (nghi ngờ scrape lặp nếu vượt)
    "max_jobs_per_run":   2000,
    # Tỷ lệ job có skill nhận diện được tối thiểu (0-1)
    "min_skill_coverage": 0.5,
    # Tỷ lệ status='ok' tối thiểu so với tổng (0-1)
    "min_ok_ratio":       0.8,
    # Tuổi dữ liệu tối đa: nếu hơn N ngày không có dữ liệu mới -> alert
    "max_data_age_days":  3,
}
