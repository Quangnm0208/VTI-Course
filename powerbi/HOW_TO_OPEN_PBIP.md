# Mở dashboard Power BI — `VTI_Skill_Insight.pbip`

## Cách mở (bật lên là chạy)
1. Cài **Power BI Desktop** (bản tháng 9/2024 trở lên — miễn phí từ Microsoft Store).
2. Mở Power BI Desktop → **File → Open report → Browse reports** → chọn
   **`powerbi/VTI_Skill_Insight.pbip`**.
3. Xong. Dashboard hiện ngay — **không hỏi nguồn dữ liệu, không cần cấu hình**.

> Vì sao không cần cấu hình: toàn bộ số liệu (ngôn ngữ, database, IDE, lương, vai
> trò) đã được **nhúng thẳng vào model** dưới dạng bảng DAX (`DATATABLE`). File
> `.pbip` không trỏ tới CSV ngoài nên mở là có dữ liệu liền.

## Trong file có gì
- **Model** (`.SemanticModel`): 11 bảng dữ liệu nhúng (gồm 3 bảng Việt Nam) +
  bảng `Measures` với 13 DAX measure (Total Respondents, Median Salary, VN Top Skill…).
- **Report** (`.Report`): **4 trang, 25 visual** theo đúng thiết kế handoff:
  - **01 Tổng quan** — 6 KPI cards + ngôn ngữ đang dùng/mong muốn + quốc gia + slicer Tín hiệu.
  - **02 Cung–cầu kỹ năng** — database đang dùng vs muốn, skill-gap, lương, IDE, vai trò.
  - **03 Việt Nam · ItViec** — 4 KPI + cầu kỹ năng VN + đối chiếu VN vs toàn cầu.
  - **04 Khuyến nghị** — ưu tiên tuyển dụng, kỹ năng emerging, rubric phỏng vấn.
- Mở `.pbip` là cả 4 trang hiện ra, dữ liệu có sẵn — chỉ việc bấm chuyển trang.

## Nếu Power BI Desktop của bạn báo lỗi định dạng report (PBIP preview)
PBIP là định dạng văn bản, đôi khi khác nhau giữa các bản Desktop. Nếu phần
**report** không mở được, **model vẫn nạp đầy đủ** — chỉ cần kéo thả field để dựng
lại visual trong ~5 phút theo `dashboard_design.md`. Hai phương án dự phòng luôn chạy:
- **`powerbi/dashboard.html`** — mở bằng trình duyệt, tương tác ngay (không cần Power BI).
- Bật preview: Power BI Desktop → **File → Options → Preview features → “Power BI
  Project (.pbip) save option”** → tích chọn → khởi động lại.

## Tái sinh file (nếu sửa số liệu)
```bash
python analysis/build_pbip.py     # đọc analysis/market_insight_data.py -> .pbip
```
