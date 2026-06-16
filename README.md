# VTI Course - Final Project: A Day in the Life of a Data Analyst
**Phân tích Kỹ năng CNTT với hệ thống scraping tự động hàng ngày**

## 📦 Sản phẩm nộp (Final Project deliverables)

| # | Yêu cầu đề bài | File trong repo |
|---|----------------|-----------------|
| A | Clean data + bảng summary | `data/processed/*.csv`, `data/clean/*.csv`, `data/processed/skill_market_insight.xlsx` |
| B | Python (collect + clean + analyze) | `src/01_collect_data.py` (GitHub API), `src/utils.py`, `src/03_analyze_data.py`, `scripts/` (scraper ItViec), `analysis/`, `notebooks/01_analysis.ipynb` |

**Nguồn dữ liệu đã thu thập (≥5.000 bản ghi, KHÔNG tính Stack Overflow):**

| Nguồn | Cách lấy | Bản ghi đã commit |
|---|---|---|
| **GitHub REST API** | `requests` API (`src/01_collect_data.py`) | **7.600 repo + 76 chỉ số nhu cầu** (`data/raw/github_*.csv`) |
| **ItViec** | Web scraping Playwright (`scripts/scrape_itviec.py`) | **1.200 dòng** (`data/itviec_jobs.csv`) |
| **VietnamWorks** | Public search API (`scripts/scrape_vietnamworks.py`) | chạy trên máy có mạng mở |
| **LinkedIn** | Public `jobs-guest` endpoint (`scripts/scrape_linkedin.py`) | chạy trên máy có mạng mở |
| Stack Overflow Survey | CSV (file gốc thả vào `data/raw/`) | 11.552 *(tùy chọn, không bắt buộc)* |

> **Tổng đã commit & verify được: 8.876 bản ghi** từ 2 nguồn live (GitHub + ItViec) — vượt mốc 5.000.
> VietnamWorks & LinkedIn có module chạy được nhưng sandbox này chặn egress (chỉ tới GitHub), nên chạy ở máy bạn/CI.
| C | SQL (CREATE/INSERT/SELECT) | `sql/analysis_queries.sql` (long-format `skill_usage` + số liệu thật), `sql/queries.sql` |
| D | Power BI dashboard | `powerbi/dashboard_design.md` (3 trang + DAX), `powerbi/*.csv` (nguồn), **`powerbi/dashboard.html`** (demo tương tác chạy được ngay) |
| E | Narrative 1 trang A4 | `reports/narrative_summary_1_page.md` |
| F | Slide ≤10 + script bảo vệ | `docs/presentation.pptx` (10 slide, chart native), `reports/slide_deck_outline.md`, `reports/defense_script.md` |
| — | Kế hoạch dự án + QA | `README_PROJECT.md` |

> **Câu hỏi phân tích** (Ngôn ngữ · Database · IDE · Kỹ năng nổi) được trả lời
> bằng số liệu thật trong dashboard, SQL, slide và notebook — tất cả lấy từ một
> nguồn duy nhất `analysis/market_insight_data.py` nên luôn khớp nhau.
>
> ⚠️ **Còn thiếu 1 input:** `Final Project.csv` (khảo sát Stack Overflow gốc)
> không commit (xem `data/README.md`). Mọi số liệu tổng hợp đã được tính từ nó.

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

- **Vượt Cloudflare bằng Playwright**: ItViec dùng Cloudflare nên `requests`
  thường bị 403 trên IP datacenter. Scraper mặc định dùng engine `playwright`
  (Chromium headless thật, có patch ẩn cờ `navigator.webdriver`, viewport
  desktop, locale `vi-VN`, timezone Asia/Ho_Chi_Minh). Tự đợi Cloudflare
  challenge ~8s nếu phát hiện title "Just a moment...".
- **Fallback**: Nếu Playwright fail liên tục -> tự rớt về engine `requests`.
  Có thể ép engine: `python scripts/scrape_itviec.py --engine requests`.
- **Cài đặt**: Trên GitHub Actions, workflow tự chạy
  `playwright install --with-deps chromium` (cài chromium + lib hệ thống).
- **Idempotent CSV**: tránh race condition khi 2 workflow chạy chồng lên nhau
  bằng `concurrency.group` trong workflow YAML.
- **Quyền commit**: workflow cần `permissions.contents: write` để push ngược.
