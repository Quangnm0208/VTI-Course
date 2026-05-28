"""
config.py — Cấu hình tập trung cho pipeline scraping ItViec.

Quy ước CSV và idempotency key dùng chung cho toàn bộ scripts.
"""

from __future__ import annotations
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

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi,en;q=0.9",
}

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
    "source_url",       # URL chi tiết job - khóa idempotent thứ 2
    "job_title",
    "company",
    "location",
    "salary",           # raw text (có thể là "Negotiable")
    "salary_min_usd",
    "salary_max_usd",
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
