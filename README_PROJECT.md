# Đồ án cuối khoá Data Analyst — Phân tích Tín hiệu Kỹ năng Thị trường Lập trình viên

**Học viên:** quangnm0208@gmail.com — VTI Academy (Data Analyst)
**Nguồn dữ liệu:** Stack Overflow Developer Survey — **11.552 lập trình viên / 135 quốc gia** (Việt Nam = 12 mẫu), median salary **$57.844**.
**Sản phẩm:** Phân tích cung-cầu kỹ năng → khuyến nghị tuyển dụng & lộ trình đào tạo cho VTI Academy, trực quan hoá bằng Power BI.

---

## 1. Project Plan — Phân chia công việc theo 7 vai trò (mốc thời gian 12 giờ)

| Giờ | Orchestrator | DS Lead | Python / Data Engineer | SQL Dev | BI Dev | Presentation Strategist | QA |
|---|---|---|---|---|---|---|---|
| **0–1** | Chốt phạm vi, chia task, dựng khung repo | Định nghĩa câu hỏi phân tích & hypothesis | Khảo sát file `Final Project.csv`, dựng `data/raw` | Lên sơ đồ bảng/staging | Khảo sát yêu cầu dashboard | Phác thảo storyline | Lập checklist QA |
| **1–3** | Theo dõi tiến độ, gỡ blocker | Xác định metric: signal, growth_pct, priority | Viết `src/` làm sạch + sinh aggregate CSV | Viết `sql/` truy vấn tổng hợp | — | Thu thập key numbers | Review schema dữ liệu |
| **3–6** | Đồng bộ giữa các nhánh | Phân tích ngôn ngữ / DB / IDE / lương | Xuất `data/clean/` + `powerbi/*.csv` | Kiểm chứng số liệu bằng SQL | Import CSV, dựng data model | Soạn dàn ý slide | Đối chiếu số liệu chéo |
| **6–9** | Ghép sản phẩm, quản lý rủi ro | Sinh insight & khuyến nghị chiến lược | Hoàn thiện notebook & pipeline | Tối ưu query, view tổng hợp | Dựng 3 trang report + DAX | Viết script thuyết trình | Test visual & filter |
| **9–11** | Rà soát toàn bộ deliverable | Review tính đúng của phân tích | Đóng gói `outputs/` & `reports/` | Bàn giao query cuối | Xuất `.pbix` + screenshot | Hoàn thiện slide demo | Chạy full QA checklist |
| **11–12** | Tổng duyệt, nộp bài | Chốt kết luận | Chốt README run | Chốt SQL artifact | Chốt dashboard | Tổng duyệt thuyết trình | Ký QA sign-off |

**Trách nhiệm chính:** Orchestrator điều phối & gom sản phẩm; DS Lead sở hữu phương pháp & insight; Data Engineer sở hữu pipeline làm sạch; SQL Dev sở hữu truy vấn kiểm chứng; BI Dev sở hữu Power BI; Presentation Strategist sở hữu câu chuyện & slide; QA sở hữu chất lượng và sign-off cuối.

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
python src/build_clean_dataset.py   # sinh lại data/clean/ & powerbi/*.csv

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
