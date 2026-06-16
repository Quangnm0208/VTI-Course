# Mở dashboard trên Power BI Desktop — 2 cách

> Cần **Power BI Desktop** (miễn phí, Microsoft Store). Power BI **Service (web)** không mở được file local.

---

## ✅ CÁCH 1 — Mở file `.pbip` (nhanh nhất, nếu Desktop bản mới)

1. Tải **cả thư mục** repo: nút xanh **Code → Download ZIP** → giải nén. (Đừng tải mỗi file `.pbip` — nó chỉ là con trỏ, cần 2 thư mục `*.Report` và `*.SemanticModel` đi kèm.)
2. Power BI Desktop → **File → Open report → Browse reports** → chọn `powerbi/VTI_Skill_Insight.pbip`.
3. Ra đủ 4 trang, dữ liệu có sẵn → **File → Save As → `.pbix`** để có bản nhị phân quen thuộc.

> Nếu báo lỗi `$schema`/`artifact`: copy **nguyên dòng lỗi** gửi lại, tôi sửa đúng phiên bản Desktop của bạn. PBIP là định dạng văn bản nên nhạy với version Desktop.

---

## ✅ CÁCH 2 — Tự dựng `.pbix` từ CSV trong ~5 phút (CHẮC CHẮN chạy mọi phiên bản)

Dữ liệu đã làm sẵn trong `powerbi/*.csv` — chỉ cần import rồi kéo-thả.

### B1. Import dữ liệu (1 lần)
**Get Data → Text/CSV** → chọn lần lượt các file trong `powerbi/` (mỗi file một query), **File Origin = 65001: Unicode (UTF-8)**, Delimiter = Comma → **Load**:
`language_signal`, `database_signal`, `ide_overall`, `salary_by_language`, `role_priority`, `country_distribution`, `dataset_overview`, `vn_itviec_skill_demand`, `vn_salary_benchmark`, `vn_vs_global_compare`.
*(Mẹo: Get Data → Folder → trỏ vào `powerbi/` để nạp nhiều file một lần.)*

### B2. Dựng visual — kéo-thả đúng bảng/cột (mỗi dòng = 1 visual)
| Visual | Loại | Trục/Field |
|---|---|---|
| Top ngôn ngữ đang dùng | Clustered bar | Axis `language_signal[language]`, Value `worked` |
| Top ngôn ngữ muốn dùng | Clustered bar | Axis `language_signal[language]`, Value `desired_next_year` |
| Skill-gap ngôn ngữ | Clustered bar | Axis `language` (Sort by `net_change`), Value `net_change` |
| Database: đang vs muốn | Clustered column | Axis `database_signal[database]`, Values `worked` + `desired_next_year` |
| Lương theo ngôn ngữ | Bar | Axis `salary_by_language[language]`, Value `median_salary` |
| IDE phổ biến | Bar | Axis `ide_overall[ide]`, Value `usage_pct` |
| Cầu kỹ năng Việt Nam | Bar | Axis `vn_itviec_skill_demand[skill]`, Value `pct_of_jobs` |
| Lương VN vs toàn cầu | Bar | Axis `vn_salary_benchmark[tier]`, Value `annual_usd_max` (thêm reference line $57.844) |
| Ưu tiên tuyển dụng | Bar | Axis `role_priority[role]`, Value `hiring_priority_score` |
| KPI Total Respondents… | Card | `dataset_overview[value]` (lọc `metric = "Total respondents"`) |

### B3. Bộ lọc (slicer) — yêu cầu đề ≥2
- Slicer 1: `language_signal[signal]` (Emerging/Stable/Declining).
- Slicer 2: `role_priority[priority_band]`.

### B4. Màu (3 màu)
Format → Data colors: chàm `#3b3fbf` · xanh lá `#10b981` (tăng) · xám `#94a3b8` (giảm/nền).

### B5. Lưu
**File → Save As → `skill_market_dashboard.pbix`**.

> Bản đặc tả đầy đủ DAX + 3 trang: xem `powerbi/dashboard_design.md` và `powerbi/handoff/powerbi_build_spec.md`.
> Giao diện đích để đối chiếu: mở `powerbi/dashboard.html`.

---

## Vì sao không giao thẳng file `.pbix`?
`.pbix` là **nhị phân**, phần data-model bên trong chỉ Power BI Desktop tạo được — **không thể sinh bằng code** ngoài Desktop. Vì vậy gói này giao: (1) `.pbip` văn bản mở-là-chạy, và (2) CSV + hướng dẫn để bạn bấm Save ra `.pbix` trong vài phút.
