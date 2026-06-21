# Tóm tắt dự án (1 trang) — Phân tích xu hướng kỹ năng IT cho VTI Academy
**Nguồn:** Stack Overflow Developer Survey **2025** · 49.191 lập trình viên · 177 quốc gia (Việt Nam 145) · median salary **$75.320/năm** · kinh nghiệm trung vị 10 năm · 68,6% có việc làm chính thức.

## 1. Bối cảnh kinh doanh
VTI Academy cần định hướng chương trình đào tạo bám sát nhu cầu tuyển dụng thực tế. Dự án phân tích khảo sát developer toàn cầu **mới nhất (2025)** để trả lời: ngôn ngữ – cơ sở dữ liệu – vai trò nào đang lên, và Academy nên ưu tiên dạy gì.

## 2. Nguồn dữ liệu & phương pháp
- **Stack Overflow Survey 2025** (benchmark toàn cầu, 49.191 dev) — nguồn chính.
- **GitHub REST API** (7.600 repo) — đo độ phổ biến công nghệ mã nguồn mở.
- **ItViec** (1.200 tin tuyển dụng) — proxy nhu cầu tuyển dụng Việt Nam.
- **Kỹ thuật thống kê:** (1) tần suất & tỷ lệ %; (2) growth-gap = `desired_next_year − worked_with`; (3) lương trung vị winsorize $300k kèm rào chắn cỡ mẫu (≥100).

## 3. Làm sạch dữ liệu
Chuẩn hoá tên cột snake_case; tách cột multi-select theo `;` về long-format (mỗi dòng một kỹ năng/người), loại NaN, khử trùng trong cùng respondent; winsorize lương. *Lưu ý phương pháp:* năm 2025 danh sách "muốn dùng" ngắn hơn "đang dùng", nên net-change phần lớn âm — vì vậy kỹ năng có net **dương** là tín hiệu tăng trưởng đặc biệt mạnh.

## 4. Phát hiện chính
- **Python & SQL là nền tảng được mong muốn nhất.** Python dẫn đầu nhu cầu năm tới (12.419 lượt), SQL (11.257), rồi HTML/CSS, JavaScript, TypeScript. → Khóa nền phải xoay quanh Python + SQL + Web.
- **Rust là "ngôi sao" tăng trưởng.** Rust được 9.262 dev muốn dùng (18,8% thị trường) và tăng **+96%** so với số đang dùng — vừa nhu cầu lớn vừa đà tăng mạnh. Kế đó: Go +42%, Zig +255%, Elixir +115% (nền nhỏ hơn).
- **PostgreSQL thống trị cơ sở dữ liệu.** Vừa được dùng nhiều nhất vừa được muốn nhất (11.863), giảm nhẹ nhất nhóm DB (−18%, "Stable"); trong khi MySQL (−52%) và SQL Server (−51%) rơi mạnh, Redis ổn định. → Dạy PostgreSQL làm chuẩn.
- **Vai trò ưu tiên & lương.** Full-stack là nhóm lớn nhất (12.351 dev → **Ưu tiên 1**), Back-end thứ nhì ($78.616 → Ưu tiên 2). Nhóm lương cao nhất: **Product/BA $122k**, DevOps $87k, Data Scientist/ML $81k — phù hợp làm khóa cao cấp.
- *(SO 2025 bỏ câu hỏi IDE — số IDE lấy từ kỳ gần nhất có hỏi, đã ghi chú trên dashboard.)*

## 5. Khuyến nghị chiến lược cho VTI Academy
1. **Lộ trình cốt lõi: Python + SQL + PostgreSQL + Git + JavaScript/TypeScript** — đúng nhóm được mong muốn nhất, đảm bảo học viên ra trường có việc.
2. **Khóa elective đón đầu: Rust và Go** (nhu cầu lớn + đà tăng + lương tốt), thêm Elixir/Zig cho lớp nâng cao.
3. **Track cao cấp theo lương:** DevOps/Cloud, Data Science/ML, Product/BA — biên lợi nhuận tốt, lương thị trường cao nhất.
4. **Việt Nam:** mẫu VN tăng lên 145 (so với 12 năm trước) nhưng vẫn nhỏ — dùng SO làm benchmark toàn cầu, kiểm chứng nhu cầu nội địa bằng ItViec/VietnamWorks.

> **Giới hạn:** khảo sát thiên về cộng đồng Stack Overflow; mẫu Việt Nam còn nhỏ → không kết luận tuyệt đối cho thị trường nội địa, cần đối chiếu nguồn tuyển dụng VN.
