# VTI Course - Final Project: A Day in the Life of a Data Analyst
**Phân tích Kỹ năng CNTT với hệ thống scraping tự động hàng ngày**

## Tổng quan

Repository này gồm 2 thành phần:

1. **Pipeline thủ công** (mục D.1 đề bài) - `src/` + `sql/` - chạy 1 lần để
   clean Final Project.csv + scrape ItViec + ghép thành 1 report.
2. **Hệ thống scraping tự động** (`scripts/` + `.github/workflows/`) - chạy
   trên GitHub Actions, cào ItViec mỗi ngày, commit dữ liệu ngược về repo.

## Cấu trúc

```
VTI-Course/
├── .github/workflows/
│   ├── daily-scrape.yml      # Cron 07:00 VN - chạy scraper + commit CSV
│   ├── data-quality.yml      # Cron 07:30 VN - check chất lượng + alert
│   └── tests.yml             # Chạy pytest mỗi lần push
├── scripts/                  # Hệ thống tự động (production)
│   ├── config.py             # Cấu hình tập trung
│   ├── scrape_itviec.py      # Scraper hàng ngày
│   ├── csv_writer.py         # UPSERT idempotent + atomic write
│   ├── cleanup_csv.py        # Dedupe + xoá pending cũ
│   └── data_quality.py       # 5 checks chất lượng dữ liệu
├── src/                      # Pipeline thủ công cho đề bài
│   ├── 01_data_collection.py
│   └── 02_data_wrangling.py
├── sql/
│   └── queries.sql           # CREATE TABLE, INSERT, SELECT
├── tests/                    # 22 unit tests
│   ├── test_csv_writer.py
│   ├── test_data_quality.py
│   └── test_scrape_itviec.py
├── data/
│   └── itviec_jobs.csv       # Dataset tích lũy (do CI tự cập nhật)
├── requirements.txt
└── README.md
```

## Hệ thống scraping tự động

### Pipeline hàng ngày

```
┌─────────────────────────────────────────────────────────────────┐
│  07:00 VN  │ daily-scrape.yml                                   │
│            │   1. scrape_itviec.py  (cào ~30 trang ItViec)      │
│            │   2. cleanup_csv.py    (dedupe)                    │
│            │   3. commit + push     (data/itviec_jobs.csv)      │
│            │   4. upload artifact                               │
├────────────┼────────────────────────────────────────────────────┤
│  07:30 VN  │ data-quality.yml                                   │
│            │   data_quality.py -> 5 checks -> markdown report   │
│            │   - PASS: log thường                               │
│            │   - WARN: artifact + log                           │
│            │   - FAIL: workflow đỏ                              │
└─────────────────────────────────────────────────────────────────┘
```

### Idempotency
Khóa upsert: `(scrape_date, source_url)`.
- Cùng job, cùng ngày -> UPDATE (không trùng lặp)
- Cùng job, khác ngày -> 2 dòng riêng (theo dõi vòng đời)
- Atomic write: `tmp file -> fsync -> os.replace` để tránh CSV bị corrupt nếu
  process bị kill giữa chừng.

### Quality checks (`scripts/data_quality.py`)
| Check | Điều kiện | Status |
|-------|-----------|--------|
| `total_jobs` | 50 ≤ jobs/lần ≤ 2000 | WARN nếu lệch |
| `ok_ratio` | ≥80% rows có status='ok' | WARN |
| `skill_coverage` | ≥50% rows có skill | WARN |
| `data_age` | Dữ liệu ≤3 ngày | FAIL nếu cũ |
| `anomalies` | Salary âm / date tương lai | WARN |

Exit code: 0 PASS, 1 WARN, 2 FAIL.

## Cách kích hoạt trên GitHub

1. Push lên GitHub (đã có sẵn workflow files).
2. Vào **Settings → Actions → General** -> chọn
   **"Read and write permissions"** cho `GITHUB_TOKEN` (để workflow tự commit CSV).
3. Vào tab **Actions** -> chọn workflow **"Daily ItViec Scrape"** -> nhấn
   **"Run workflow"** để chạy ngay (không đợi cron).
4. Sau khi chạy xong, file `data/itviec_jobs.csv` sẽ tự xuất hiện trong repo.

### Trigger thủ công với tham số
Tab Actions → Daily ItViec Scrape → Run workflow → nhập `pages` (vd 5 để test nhanh).

## Chạy local

```bash
pip install -r requirements.txt

# Scrape (mặc định 30 trang)
python scripts/scrape_itviec.py --pages 5

# Cleanup
python scripts/cleanup_csv.py --apply

# Quality check
python scripts/data_quality.py --report quality_report.md

# Tests
pytest tests/ -v
```

## Pipeline thủ công cho đề bài

```bash
# Đặt Final Project.csv vào data/raw/ rồi:
python src/01_data_collection.py        # Scrape + stage CSV
python src/02_data_wrangling.py         # Clean + ghép report
sqlite3 data/clean/skills.db < sql/queries.sql
```

Đầu ra: `data/clean/skill_report.csv` + `.xlsx` (3 sheet) + `skills.db`.

## Lưu ý kỹ thuật

- **ItViec chống bot**: Một số IP (Cloudflare datacenter, container) có thể bị
  ItViec trả 403. Trên GitHub-hosted runner thường vẫn cào được nhưng nếu gặp
  block, có thể cần:
  - Tăng độ tinh vi User-Agent / thêm session cookies
  - Dùng proxy (self-hosted runner ở VN)
  - Hoặc thay bằng VietnamWorks / TopCV làm nguồn dự phòng.
- **Idempotent CSV**: tránh race condition khi 2 workflow chạy chồng lên nhau
  bằng `concurrency.group` trong workflow YAML.
- **Quyền commit**: workflow cần `permissions.contents: write` để push ngược.
