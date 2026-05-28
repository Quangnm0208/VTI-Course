# Final Project: A Day in the Life of a Data Analyst
**Phân tích Kỹ năng CNTT - VTI Academy**

## Tổng quan
Pipeline gồm 3 bước:
1. **Scrape ItViec** (`src/01_data_collection.py`) - lấy tin tuyển dụng IT tại VN.
2. **Clean + ghép** (`src/02_data_wrangling.py`) - làm sạch khảo sát Stack Overflow
   (Final Project.csv) + ItViec rồi ghép thành **1 report tổng hợp**.
3. **Truy vấn SQL** (`sql/queries.sql`) - CREATE TABLE / INSERT / SELECT cho
   4 câu hỏi phân tích.

## Cấu trúc
```
VTI-Course/
├── src/
│   ├── 01_data_collection.py    # Web scraping ItViec + stage CSV khảo sát
│   └── 02_data_wrangling.py     # Clean & ghép thành report
├── sql/
│   └── queries.sql              # CREATE TABLE, INSERT, SELECT
├── data/
│   ├── raw/                     # Final Project.csv + itviec_jobs_raw.csv
│   └── clean/                   # report cuối (CSV + Excel + SQLite)
├── requirements.txt
└── README.md
```

## Chạy pipeline

```bash
# 1. Cài thư viện
pip install -r requirements.txt

# 2. Đặt file khảo sát vào data/raw/
cp /path/to/Final\ Project.csv data/raw/

# 3. Scrape ItViec
python src/01_data_collection.py

# 4. Clean + ghép report
python src/02_data_wrangling.py

# 5. Chạy SQL (SQLite)
sqlite3 data/clean/skills.db < sql/queries.sql
```

## File đầu ra (data/clean/)
| File | Mô tả |
|------|-------|
| `survey_clean.csv` | Khảo sát Stack Overflow đã làm sạch |
| `itviec_jobs_clean.csv` | Tin tuyển dụng ItViec đã làm sạch |
| `skill_report.csv` | **Report tổng hợp** (long-format) - dùng cho Power BI |
| `skill_report.xlsx` | Bản Excel với 3 sheet: report / summary / itviec |
| `skill_summary.csv` | Pivot: skill x source -> số lượt mention |
| `skills.db` | SQLite chứa 4 bảng để truy vấn SQL |

## Công cụ
Python (pandas, requests, BeautifulSoup) - SQL (SQLite) - Power BI
