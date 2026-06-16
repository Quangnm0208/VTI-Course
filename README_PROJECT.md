# Đồ án cuối khoá Data Analyst — Phân tích Tín hiệu Kỹ năng Thị trường Lập trình viên

**Học viên:** quangnm0208@gmail.com — VTI Academy (Data Analyst)
**Nguồn dữ liệu:** Stack Overflow Developer Survey — **11.552 lập trình viên / 135 quốc gia** (Việt Nam = 12 mẫu), median salary **$57.844**.
**Sản phẩm:** Phân tích cung-cầu kỹ năng → khuyến nghị tuyển dụng & lộ trình đào tạo cho VTI Academy, trực quan hoá bằng Power BI.

---

## 1. Kế hoạch thực hiện — 6 giai đoạn (mốc thời gian 12 giờ)

| Giờ | Giai đoạn | Công việc chính | Đầu ra |
|---|---|---|---|
| **0–1** | Khung & phạm vi | Chốt câu hỏi phân tích, dựng khung repo, khảo sát `Final Project.csv` | Cấu trúc thư mục, checklist |
| **1–3** | Thu thập & làm sạch | Viết `src/` chuẩn hoá cột, tách multi-select, xử lý thiếu, sinh aggregate CSV | `data/clean/`, `data/processed/` |
| **3–6** | Phân tích | Tín hiệu ngôn ngữ / database / IDE / lương, growth_gap, ưu tiên vai trò | Notebook + bảng tổng hợp |
| **6–9** | SQL & kiểm chứng | Viết `sql/` (CREATE/INSERT/SELECT), đối chiếu số liệu chéo với phân tích | `sql/analysis_queries.sql` |
| **9–11** | Trực quan hoá | Dựng data model Power BI (3 trang, DAX), demo `dashboard.html` | `powerbi/`, `.pbix` |
| **11–12** | Báo cáo & nộp | Narrative 1 trang, slide ≤10, script bảo vệ, rà soát QA | `reports/`, `docs/presentation.pptx` |

**Nguyên tắc xuyên suốt:** mỗi insight gắn với số liệu cụ thể, mỗi khuyến nghị gắn với insight; toàn bộ con số lấy từ một nguồn duy nhất để dashboard – SQL – slide – notebook luôn khớp nhau.

---

## 2. Cấu trúc thư mục (Folder Structure)

```
VTI-Course/
├── README.md                       # Giới thiệu repo
├── README_PROJECT.md               # (file này) Kế hoạch dự án + cách chạy + QA
├── requirements.txt                # Thư viện Python
├── data/
│   ├── raw/                        # Final Project.csv (KHẢO SÁT GỐC - người dùng tự thả vào, xem mục 4)
│   ├── processed/                  # Dữ liệu trung gian sau làm sạch
│   └── clean/                      # Aggregate CSV đã chốt + skill_market_insight.xlsx
├── notebooks/                      # Notebook phân tích (EDA, signal, salary...)
├── src/                            # Code Python: làm sạch & sinh aggregate
├── sql/                            # Truy vấn SQL kiểm chứng/tổng hợp
├── powerbi/                        # CSV nguồn + dashboard.html (demo) + .pbix + dashboard_design.md
├── reports/                        # Báo cáo, slide, ảnh chụp dashboard
├── outputs/                        # Kết quả xuất ra (bảng, hình, file phái sinh)
└── docs/                           # Tài liệu phương pháp luận
```

---

## 3. How to run — Quickstart

```bash
# 1) Tạo môi trường ảo và cài thư viện
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) (Nếu có raw) Thả file khảo sát gốc vào data/raw/Final Project.csv
#    rồi chạy pipeline làm sạch để tái tạo dữ liệu dòng-lệnh:
python src/03_analyze_data.py        # sinh lại data/processed/ summary tables

# 3) Xem dashboard demo (chạy ngay, không cần Power BI):
#    Mở powerbi/dashboard.html bằng trình duyệt.

# 4) Dựng file .pbix:
#    Mở Power BI Desktop -> làm theo powerbi/dashboard_design.md
```

> Các aggregate CSV trong `powerbi/` và `data/clean/` **đã được commit sẵn** — có thể mở `dashboard.html` và dựng `.pbix` ngay mà không cần raw.

---

## 4. QA Review Checklist

Trạng thái: ✅ = đã xong · ⚠️ = điểm còn thiếu đã biết (xem ghi chú).

### 4.1 Kỹ thuật (Technical)
- [x] ✅ Cấu trúc repo rõ ràng, có `.gitignore` cho dữ liệu lớn/nhạy cảm.
- [x] ✅ `requirements.txt` đầy đủ thư viện chạy pipeline.
- [x] ✅ Code làm sạch & sinh aggregate nằm trong `src/`, tách bạch khỏi notebook.
- [ ] ⚠️ **Raw `Final Project.csv` chưa được commit** → dataset dòng-lệnh (row-level clean) phải được người dùng tái tạo bằng cách thả file vào `data/raw/` rồi chạy `src/`. (Xem ghi chú gap bên dưới.)

### 4.2 Phân tích (Analytical)
- [x] ✅ Các con số gốc đã được kiểm chứng: 11.552 respondents / 135 countries / VN=12 / median $57.844.
- [x] ✅ Tín hiệu ngôn ngữ (Emerging: Rust +369,5% · Kotlin +152,9% · Go +148,3% · TypeScript +26,6%).
- [x] ✅ Tín hiệu database (PostgreSQL +5,6% dẫn đầu & tăng · MySQL −40% · MongoDB/Redis/Elasticsearch tăng).
- [x] ✅ Lương & vai trò (DevOps median cao nhất $71.036; Full-stack Priority 1).
- [x] ✅ Mọi số liệu phân tích **đã được suy ra và commit** trong `data/clean/` + `powerbi/`.

### 4.3 Power BI
- [x] ✅ Đặc tả `powerbi/dashboard_design.md` đầy đủ 3 trang, ≥ 5 visual, ≥ 2 slicer, ≥ 6 DAX.
- [x] ✅ 12 CSV nguồn sẵn sàng để Get Data > Text/CSV (UTF-8).
- [x] ✅ `powerbi/dashboard.html` chạy được làm demo + nguồn ảnh chụp.
- [ ] ⚠️ File nhị phân `.pbix` cần dựng cuối cùng trong Power BI Desktop (theo dashboard_design.md) — không tạo được bằng code.

### 4.4 Báo cáo & Thuyết trình (Reporting)
- [x] ✅ Khuyến nghị chiến lược (ngắn/trung/dài hạn) trong `strategic_recommendations.csv`.
- [x] ✅ Lộ trình đào tạo & rubric phỏng vấn (`training_roadmap.csv`, `interview_rubric.csv`).
- [x] ✅ Storyline rõ: từ dữ liệu → tín hiệu kỹ năng → khuyến nghị tuyển dụng/đào tạo cho VTI.

### Ghi chú điểm còn thiếu (known gap — trung thực)
File khảo sát gốc **`Final Project.csv`** (Stack Overflow Developer Survey) **không được commit** vào repo (kích thước lớn / điều khoản dữ liệu). Vì vậy **bộ dữ liệu sạch ở mức từng dòng (row-level) phải được người dùng tái tạo**: thả `Final Project.csv` vào `data/raw/` rồi chạy script trong `src/`.
**Toàn bộ con số phân tích tổng hợp đã được suy ra sẵn và đã commit** trong `data/clean/` và `powerbi/`, nên việc mở dashboard demo và dựng `.pbix` không bị chặn bởi gap này.
