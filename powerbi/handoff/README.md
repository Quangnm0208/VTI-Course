# VTI Skill Market — Power BI Handoff

Gói bàn giao để đội dev **dựng lại dashboard trong Power BI Desktop** với dữ liệu mới.
Toàn bộ số liệu là dữ liệu thật đã làm sạch — **không bịa**.

## Nội dung gói

```
VTI-PowerBI-Handoff/
├── README.md                     # file này
├── powerbi_build_spec.md         # ĐẶC TẢ DỰNG BÁO CÁO (đọc file này trước)
├── data/                         # 15 nguồn CSV (import vào Power BI)
│   ├── dataset_overview.csv
│   ├── language_signal.csv
│   ├── database_signal.csv
│   ├── ide_overall.csv
│   ├── ide_by_role.csv
│   ├── salary_by_language.csv
│   ├── role_priority.csv
│   ├── country_distribution.csv
│   ├── jd_keyword_map.csv
│   ├── training_roadmap.csv
│   ├── interview_rubric.csv
│   ├── strategic_recommendations.csv
│   ├── vn_itviec_skill_demand.csv     # MỚI — cầu kỹ năng VN (ItViec, 1.200 JD)
│   ├── vn_salary_benchmark.csv        # MỚI — lương VN theo cấp vs mốc toàn cầu
│   ├── vn_vs_global_compare.csv       # MỚI — đối chiếu cầu VN vs toàn cầu
│   └── itviec_jobs_raw.csv            # Dữ liệu thô ItViec (1.200 dòng) để tự tổng hợp lại
└── reference/
    └── dashboard_reference.html       # Bản dashboard tương tác — DÙNG LÀM MẪU GIAO DIỆN
```

## Cách dùng
1. Mở `reference/dashboard_reference.html` bằng trình duyệt để xem **giao diện đích** (4 trang, bộ lọc, màu sắc).
2. Đọc `powerbi_build_spec.md` — có sơ đồ model, đo DAX, bản đồ visual→nguồn, các bước dựng `.pbix`.
3. Import 15 CSV trong `data/` (UTF-8, delimiter = comma) → dựng theo spec → Save As `.pbix`.

## Quy ước số liệu (đọc kỹ — tránh hiểu nhầm)
- **Toàn cầu** = Stack Overflow Developer Survey (11.552 dev / 135 quốc gia / median $57.844).
- **Việt Nam (cầu)** = scrape ItViec ngày **2026-05-28**, 1.200 JD. `pct_of_jobs` = % JD có nhắc kỹ năng đó.
- **Việt Nam (lương)**: ItViec **ẩn lương** — 0/1.200 JD công khai. Vì vậy số lương VN trong `vn_salary_benchmark.csv` lấy từ **báo cáo công khai TopDev / Reco / Glassdoor 2024–2026** (cột `source`), KHÔNG suy từ ItViec. Mốc toàn cầu $57.844 từ Stack Overflow.
