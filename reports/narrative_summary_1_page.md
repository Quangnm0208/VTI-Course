# Tóm tắt dự án: Một ngày của Data Analyst — Phân tích xu hướng kỹ năng IT

## 1. Bối cảnh kinh doanh
VTI Academy cần định hướng chương trình đào tạo bám sát nhu cầu tuyển dụng thực tế của thị trường lập trình viên. Dự án phân tích dữ liệu khảo sát toàn cầu để trả lời: ngôn ngữ, cơ sở dữ liệu và công cụ nào đang lên, vai trò nào nên ưu tiên tuyển sinh, và lương phản ánh nhu cầu ra sao — từ đó giúp Academy ưu tiên ngân sách xây khóa học và marketing tuyển sinh.

## 2. Nguồn dữ liệu & phương pháp
- **Stack Overflow Developer Survey** (benchmark toàn cầu, CSV 90 cột): 11.552 lập trình viên, 135 quốc gia.
- **ItViec job postings** (proxy nhu cầu tuyển dụng Việt Nam, scrape hằng ngày bằng Playwright; lương bị ẩn sau đăng nhập nên đánh dấu `login_required` thay vì ước đoán).
- **Cổng đào tạo** (nguồn cung khóa học, tùy chọn).
- **Kỹ thuật thống kê:** (1) đếm tần suất & tỷ lệ phần trăm; (2) net-change / growth-gap = `desired_next_year − worked_with`; (3) lương trung vị có rào chắn cỡ mẫu, winsorize tại $300k vì lương tự khai có ngoại lai.

## 3. Cách làm sạch dữ liệu
Cột multi-select (ngôn ngữ, database, IDE) được tách theo dấu `;` thành định dạng long (mỗi dòng một kỹ năng/người), loại bỏ NaN, khử trùng lặp trong cùng một người trả lời. Lương được winsorize ở $300k và luôn báo cáo kèm cỡ mẫu để tránh kết luận trên nhóm quá nhỏ.

## 4. Phát hiện chính
- **Python & TypeScript là tương lai gần.** Python tăng +15,1% (4.611→5.309), TypeScript +26,6% (3.269→4.140), trong khi JavaScript −23,7%, Java −34,4%, PHP −50%. *Ý nghĩa:* khóa học cốt lõi nên xoay quanh Python/TypeScript thay vì PHP/Java thuần.
- **Ngôn ngữ tăng trưởng nóng nhưng nền nhỏ.** Rust +369,5%, Kotlin +152,9%, Go +148,3%, WebAssembly +941,9%. *Ý nghĩa:* mở khóa nâng cao (elective) cho học viên đã có nền, không đưa vào lộ trình cơ bản.
- **Database: PostgreSQL, MongoDB, Redis lên; MySQL & Oracle xuống.** PostgreSQL +5,6% (dẫn đầu nhu cầu), Redis +33,5%, MongoDB +21,1%; MySQL −40%, Oracle −50%. *Ý nghĩa:* dạy PostgreSQL làm chuẩn, bổ sung NoSQL (MongoDB/Redis).
- **VS Code thống trị (~55%) gần như mọi vai trò;** Jupyter dẫn đầu nhóm Data Scientist (390), Vim là công cụ #2 của DevOps. *Ý nghĩa:* chuẩn hóa môi trường thực hành quanh VS Code + Jupyter cho học phần dữ liệu.
- **Vai trò ưu tiên tuyển sinh: Full-stack (6.928 dev, $59.000, Ưu tiên 1)** và Back-end (6.290, $56.715). DevOps lương cao nhất ($71.036). *Ý nghĩa:* dồn năng lực vào lộ trình Full-stack/Back-end; DevOps là khóa cao cấp biên lợi nhuận tốt.

## 5. Khuyến nghị chiến lược
1. **Tái cấu trúc lộ trình cốt lõi quanh Python + TypeScript + PostgreSQL**, giảm dần PHP/Java thuần — bám đúng nhu cầu tăng trưởng và vai trò Full-stack/Back-end ưu tiên 1–2.
2. **Mở các khóa elective ngắn cho kỹ năng tăng trưởng nóng** (Go, Rust, Kotlin, MongoDB/Redis, DevOps) hướng đến học viên đã có nền, tận dụng mức lương cao để định giá premium.
3. **Xác thực mọi quyết định cho thị trường Việt Nam bằng ItViec**, không kết luận từ 12 mẫu khảo sát Việt Nam; dùng Stack Overflow làm benchmark toàn cầu, ItViec làm tín hiệu địa phương.

> **Giới hạn quan trọng:** Việt Nam chỉ có 12 phản hồi khảo sát → coi Stack Overflow là benchmark toàn cầu, xác thực đặc thù Việt Nam bằng ItViec. Không kết luận quá mức về Việt Nam.
