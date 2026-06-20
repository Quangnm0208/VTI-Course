# Thư mục dữ liệu

```
data/
├── raw/            # (gitignored) DỮ LIỆU GỐC — bạn tự đặt vào, không commit
│   └── Final Project.csv      <-- THIẾU: hãy đặt file khảo sát Stack Overflow vào đây
├── processed/      # Sản phẩm phân tích (đã commit)
│   ├── language_summary.csv
│   ├── database_summary.csv
│   ├── ide_summary.csv
│   ├── emerging_skills_summary.csv
│   ├── skill_market_insight.xlsx
│   └── clean_it_skills_data.csv   <-- chỉ sinh ra khi đã có raw (xem dưới)
├── clean/          # Bảng tổng hợp dùng cho Power BI / SQL (đã commit)
└── itviec_jobs.csv # Tin tuyển dụng ItViec do scraper thu thập (đã commit)
```

## ⚠️ File còn thiếu để chạy pipeline THẬT end-to-end

`Final Project.csv` (khảo sát Stack Overflow, ~11.552 dòng × 90 cột) **không được
commit** vì là dữ liệu gốc. Notebook và toàn bộ con số tổng hợp đã được tính từ
chính file này (kết quả lưu sẵn trong `notebooks/01_analysis.ipynb` và
`analysis/market_insight_data.py`).

Để tái tạo `clean_it_skills_data.csv` ở cấp dòng (row-level) và chạy lại từ đầu:

```bash
# 1. Đặt file vào data/raw/Final Project.csv  (hoặc final_project.csv)
# 2. Chạy pipeline:
python src/03_analyze_data.py        # sinh clean_it_skills_data.csv + summary
jupyter notebook notebooks/01_analysis.ipynb   # chạy phân tích đầy đủ
```

Không có file raw, `src/03_analyze_data.py` vẫn chạy được và xuất các bảng summary
từ bộ số liệu tổng hợp đã chốt (kết quả đã tính sẵn từ khảo sát gốc).
