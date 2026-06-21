# Slide Deck Outline — Một ngày của Data Analyst: Phân tích xu hướng kỹ năng IT
*10 slide, dùng số liệu thực từ Stack Overflow Developer Survey 2025 (49.191 lập trình viên, 177 quốc gia).*

---

## Slide 1 — Tiêu đề & Bối cảnh
- **Title:** Một ngày của Data Analyst — Phân tích xu hướng kỹ năng IT cho VTI Academy
- **Key message:** Phân tích 49.191 lập trình viên trên 177 quốc gia để định hướng chương trình đào tạo bám sát nhu cầu thị trường.
- **Suggested visual:** Ảnh bìa + 3 con số lớn (49.191 dev / 177 quốc gia / lương trung vị 75.320).
- **Speaker notes:** VTI Academy cần đào tạo đúng kỹ năng đang tăng nhu cầu. Dự án trả lời ngôn ngữ/database/công cụ nào nên ưu tiên và vai trò nào nên dồn tuyển sinh. Mục tiêu là quyết định dựa trên dữ liệu, không cảm tính.

## Slide 2 — Phương pháp & Pipeline dữ liệu
- **Title:** Nguồn dữ liệu & quy trình phân tích
- **Key message:** Ba nguồn bổ trợ nhau — benchmark toàn cầu, tín hiệu tuyển dụng Việt Nam và nguồn cung khóa học.
- **Suggested visual:** Sơ đồ pipeline: Stack Overflow CSV (90 cột) + ItViec (Playwright) + Cổng đào tạo → Làm sạch → Thống kê → Power BI.
- **Speaker notes:** Stack Overflow là benchmark toàn cầu; ItViec scrape hằng ngày làm proxy nhu cầu Việt Nam (lương ẩn sau đăng nhập, đánh dấu login_required thay vì ước đoán). Kỹ thuật thống kê: tần suất & %, growth-gap = desired − worked, lương trung vị winsorize tại $300k kèm rào chắn cỡ mẫu.

## Slide 3 — Tổng quan bộ dữ liệu
- **Title:** Chân dung người trả lời
- **Key message:** Mẫu nghiêng về phương Tây, làm full-time, nhiều kinh nghiệm — mạnh để làm benchmark toàn cầu.
- **Suggested visual:** Bản đồ/biểu đồ cột phân bổ quốc gia + thẻ chỉ số.
- **Speaker notes:** 96,2% làm full-time, kinh nghiệm coding chuyên nghiệp trung vị 5 năm, trung bình dùng 5,2 ngôn ngữ và muốn học 4,9. Top quốc gia: Mỹ 27,5%, Ấn Độ 7,9%, Anh 7,3%, Đức 6,2%. Việt Nam chỉ 145 phản hồi nên không kết luận riêng cho Việt Nam từ khảo sát.

## Slide 4 — Xu hướng ngôn ngữ lập trình
- **Title:** Ngôn ngữ nào đang được dùng nhiều nhất?
- **Key message:** JavaScript, HTML/CSS, SQL dẫn đầu hiện tại nhưng Python và TypeScript đang vươn lên mạnh.
- **Suggested visual:** Biểu đồ cột ngang xếp hạng "worked with" (JavaScript 8.805, HTML/CSS 7.920, SQL 7.213, Python 4.611, Bash 4.694, Java 4.556, C# 4.346).
- **Speaker notes:** Nền tảng web (JS/HTML/SQL) vẫn là kỹ năng phổ biến nhất nên giữ trong lộ trình cơ bản. Tuy nhiên độ phổ biến hiện tại không bằng xu hướng tương lai — slide sau cho thấy bức tranh đang dịch chuyển.

## Slide 5 — Nhu cầu ngôn ngữ tương lai (hiện tại vs mong muốn)
- **Title:** Ngôn ngữ nào lập trình viên MUỐN học năm tới?
- **Key message:** Python (+15,1%) và TypeScript (+26,6%) là tương lai gần; nhóm tăng trưởng nóng (Rust, Go, Kotlin) nền còn nhỏ.
- **Suggested visual:** Biểu đồ growth-gap (desired − worked), thanh xanh/đỏ: tăng vs giảm.
- **Speaker notes:** Tăng: Python +15,1%, TypeScript +26,6%, Go +148,3%, Kotlin +152,9%, Rust +369,5%, WebAssembly +941,9%. Giảm: JavaScript −23,7%, Java −34,4%, PHP −50%, Bash −33,2%. Khuyến nghị: cốt lõi đặt vào Python/TypeScript, mở elective cho Go/Rust/Kotlin cho học viên đã có nền — đừng đưa vào lộ trình cơ bản.

## Slide 6 — Xu hướng cơ sở dữ liệu
- **Title:** Database nào đang lên, đang xuống?
- **Key message:** PostgreSQL, MongoDB, Redis tăng nhu cầu; MySQL và Oracle giảm mạnh.
- **Suggested visual:** Biểu đồ growth-gap database song song với slide 5.
- **Speaker notes:** PostgreSQL +5,6% (dẫn đầu nhu cầu mong muốn 4.386), Redis +33,5%, MongoDB +21,1%, Elasticsearch +46,4%; ngược lại MySQL −40%, Oracle −50%, MS SQL Server −34,1%. Khuyến nghị: dạy PostgreSQL làm chuẩn SQL, bổ sung học phần NoSQL (MongoDB/Redis) thay cho MySQL/Oracle thuần.

## Slide 7 — Xu hướng IDE / Môi trường phát triển
- **Title:** Lập trình viên làm việc bằng công cụ gì?
- **Key message:** VS Code thống trị (~55%) gần như mọi vai trò; Jupyter dẫn đầu nhóm Data Scientist.
- **Suggested visual:** Biểu đồ cột thị phần IDE + chú thích công cụ đặc thù theo vai trò.
- **Speaker notes:** Visual Studio Code ~55% trên hầu hết vai trò, sau đó là Visual Studio, Notepad++, IntelliJ, Vim, PyCharm, Sublime. IPython/Jupyter đứng đầu nhóm Data Scientist (390); Vim là công cụ #2 của DevOps. Khuyến nghị: chuẩn hóa thực hành quanh VS Code, dùng Jupyter cho học phần dữ liệu.

## Slide 8 — Tổng quan Dashboard Power BI
- **Title:** Dashboard tương tác cho ra quyết định
- **Key message:** Dashboard cho phép lọc theo vai trò, kỹ năng, lương để Academy ra quyết định nhanh.
- **Suggested visual:** Screenshot Power BI: KPI cards (49.191 dev, lương trung vị 75.320), biểu đồ growth-gap, bảng lương theo ngôn ngữ và vai trò.
- **Speaker notes:** Dashboard gồm trang tổng quan, xu hướng ngôn ngữ/database, lương theo ngôn ngữ (Clojure $93k, Go $80k, Python $64k... PHP $43k) và ưu tiên vai trò. Người dùng tự lọc theo nhu cầu thay vì đọc báo cáo tĩnh, hỗ trợ quyết định lặp lại theo mùa tuyển sinh.

## Slide 9 — Khuyến nghị chiến lược
- **Title:** Ba khuyến nghị cho VTI Academy
- **Key message:** Tập trung lõi vào Python/TypeScript/PostgreSQL, mở elective kỹ năng nóng, và xác thực Việt Nam bằng ItViec.
- **Suggested visual:** 3 thẻ khuyến nghị kèm vai trò ưu tiên (Full-stack 6.928/$59.000/Ưu tiên 1; Back-end 6.290/$56.715; DevOps $71.036).
- **Speaker notes:** (1) Tái cấu trúc lộ trình cốt lõi quanh Python+TypeScript+PostgreSQL, giảm PHP/Java thuần. (2) Mở elective ngắn cho Go/Rust/Kotlin/MongoDB/Redis/DevOps, định giá premium nhờ lương cao. (3) Mọi quyết định cho Việt Nam phải xác thực bằng ItViec, không suy từ 145 mẫu khảo sát.

## Slide 10 — Q&A
- **Title:** Cảm ơn — Hỏi & Đáp
- **Key message:** Sẵn sàng trao đổi về nguồn dữ liệu, phương pháp và tính đại diện cho Việt Nam.
- **Suggested visual:** Slide cảm ơn + thông tin liên hệ + nhắc lại 3 con số chủ chốt.
- **Speaker notes:** Chủ động nêu giới hạn cỡ mẫu Việt Nam (145 phản hồi) và cách khắc phục bằng ItViec để thể hiện tư duy phản biện. Sẵn sàng giải thích kỹ thuật xử lý multi-select và winsorize lương.
