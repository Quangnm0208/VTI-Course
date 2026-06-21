# Slide Deck Outline — Một ngày của Data Analyst: Phân tích xu hướng kỹ năng IT
*10 slide, dùng số liệu thực từ Stack Overflow Developer Survey 2025 (49.191 lập trình viên, 177 quốc gia).*

---

## Slide 1 — Tiêu đề & Bối cảnh
- **Title:** Một ngày của Data Analyst — Phân tích xu hướng kỹ năng IT cho VTI Academy
- **Key message:** Phân tích 49.191 lập trình viên trên 177 quốc gia để định hướng chương trình đào tạo bám sát nhu cầu thị trường.
- **Suggested visual:** Ảnh bìa + 3 con số lớn (49.191 dev / 177 quốc gia / lương trung vị $75.320).
- **Speaker notes:** VTI Academy cần đào tạo đúng kỹ năng đang tăng nhu cầu. Dự án trả lời ngôn ngữ/database/vai trò nào nên ưu tiên — quyết định dựa trên dữ liệu mới nhất 2025.

## Slide 2 — Phương pháp & Pipeline dữ liệu
- **Title:** Nguồn dữ liệu & quy trình phân tích
- **Key message:** Ba nguồn bổ trợ — benchmark toàn cầu (SO 2025), nhu cầu mã nguồn mở (GitHub), tín hiệu tuyển dụng Việt Nam (ItViec).
- **Suggested visual:** Sơ đồ pipeline: Stack Overflow 2025 + GitHub API + ItViec → Làm sạch (Pandas) → Thống kê → Power BI.
- **Speaker notes:** SO 2025 (49.191 dev) là benchmark; GitHub API (7.600 repo) đo độ phổ biến công nghệ; ItViec (1.200 tin) làm proxy Việt Nam. Thống kê: tần suất & %, growth-gap = desired − worked, lương trung vị winsorize $300k kèm rào chắn cỡ mẫu.

## Slide 3 — Tổng quan bộ dữ liệu
- **Title:** Chân dung người trả lời
- **Key message:** Mẫu lớn, nhiều kinh nghiệm — mạnh để làm benchmark toàn cầu.
- **Suggested visual:** Biểu đồ cột phân bổ quốc gia + thẻ chỉ số.
- **Speaker notes:** Kinh nghiệm trung vị 10 năm, 68,6% có việc làm chính thức, trung bình dùng 4,0 ngôn ngữ. Top quốc gia: Mỹ 14,7%, Đức 6,1%, Ấn Độ 5,2%, Anh 4,2%. Việt Nam 145 phản hồi (tăng từ 12 năm trước) nhưng vẫn nhỏ → không kết luận riêng cho VN từ khảo sát.

## Slide 4 — Xu hướng ngôn ngữ lập trình
- **Title:** Ngôn ngữ nào được dùng & được muốn nhiều nhất?
- **Key message:** Python và SQL là nền tảng được mong muốn nhất năm tới.
- **Suggested visual:** Biểu đồ cột ngang "muốn dùng năm tới": Python 12.419, SQL 11.257, HTML/CSS 10.661, JavaScript 10.581, TypeScript 10.099.
- **Speaker notes:** Python vượt JavaScript trở thành ngôn ngữ được mong muốn nhất — phản ánh sức hút của Data/AI. SQL đứng nhì, khẳng định kỹ năng dữ liệu là nền tảng. Bộ Web (JS/TS/HTML) vẫn rất mạnh → giữ trong lộ trình cốt lõi.

## Slide 5 — Nhu cầu tương lai & kỹ năng nổi (growth-gap)
- **Title:** Kỹ năng nào đang tăng trưởng?
- **Key message:** Rust là ngôi sao: nhu cầu lớn + đà tăng mạnh nhất; Go theo sau.
- **Suggested visual:** Biểu đồ growth-gap (desired − worked), tô xanh phần tăng.
- **Speaker notes:** Lưu ý phương pháp: 2025 danh sách "muốn dùng" ngắn hơn "đang dùng" nên net phần lớn âm — kỹ năng net **dương** là tín hiệu mạnh. Emerging: **Rust +96%** (9.262 muốn dùng, 18,8% thị trường), **Go +42%**, Zig +255%, Elixir +115% (nền nhỏ). Khuyến nghị: cốt lõi Python/SQL/TypeScript; mở elective Rust/Go cho học viên đã có nền.

## Slide 6 — Xu hướng cơ sở dữ liệu
- **Title:** Database nào nên dạy làm chuẩn?
- **Key message:** PostgreSQL thống trị; MySQL/SQL Server giảm mạnh.
- **Suggested visual:** Biểu đồ cột "đang dùng vs muốn dùng" theo database.
- **Speaker notes:** PostgreSQL vừa được dùng nhiều nhất vừa được muốn nhất (11.863) và giảm nhẹ nhất nhóm DB (−18%, "Stable"); Redis ổn định. Ngược lại MySQL −52%, MS SQL Server −51%, MongoDB −30%. Khuyến nghị: dạy **PostgreSQL làm chuẩn SQL**, thêm Redis cho phần caching/NoSQL.

## Slide 7 — IDE / Môi trường phát triển
- **Title:** Lập trình viên làm việc bằng công cụ gì?
- **Key message:** VS Code vẫn thống trị môi trường phát triển.
- **Suggested visual:** Biểu đồ cột thị phần IDE (kỳ khảo sát gần nhất có hỏi IDE).
- **Speaker notes:** *Lưu ý trung thực:* SO 2025 đã bỏ câu hỏi IDE, nên số liệu IDE lấy từ kỳ gần nhất có hỏi (Visual Studio Code dẫn đầu ~55%, sau đó Visual Studio, IntelliJ, Vim, PyCharm). Khuyến nghị: chuẩn hóa thực hành quanh VS Code; dùng Jupyter cho học phần dữ liệu.

## Slide 8 — Tổng quan Dashboard Power BI
- **Title:** Dashboard tương tác cho ra quyết định
- **Key message:** Dashboard cho phép lọc theo tín hiệu, vai trò, lương để Academy quyết định nhanh.
- **Suggested visual:** Screenshot Power BI: KPI (49.191 dev, lương trung vị $75.320), growth-gap, lương theo ngôn ngữ, ưu tiên vai trò.
- **Speaker notes:** Dashboard gồm 4 trang: Tổng quan, Cung–cầu kỹ năng, Việt Nam (ItViec), Khuyến nghị. Lương theo ngôn ngữ: Ruby $103k, Erlang $100k, Elixir $99k, Swift $92k... — nhóm ngôn ngữ chuyên sâu/lâu năm trả cao nhất. Người dùng tự lọc thay vì đọc báo cáo tĩnh.

## Slide 9 — Khuyến nghị chiến lược
- **Title:** Khuyến nghị cho VTI Academy
- **Key message:** Cốt lõi Python/SQL/PostgreSQL, elective Rust/Go, track cao cấp theo lương.
- **Suggested visual:** Thẻ khuyến nghị + ưu tiên vai trò (Full-stack 12.351/$71.078/Ưu tiên 1; Back-end 6.453/$78.616/Ưu tiên 2; Product/BA $122k).
- **Speaker notes:** (1) Lộ trình cốt lõi Python+SQL+PostgreSQL+Git+JS/TS — đúng nhóm được muốn nhất. (2) Elective đón đầu Rust/Go (nhu cầu + đà tăng + lương tốt), thêm Elixir/Zig nâng cao. (3) Track cao cấp DevOps/Data Science/Product-BA — lương thị trường cao nhất. (4) Xác thực Việt Nam bằng ItViec, không suy từ 145 mẫu.

## Slide 10 — Q&A
- **Title:** Cảm ơn — Hỏi & Đáp
- **Key message:** Sẵn sàng trao đổi về nguồn dữ liệu, phương pháp và tính đại diện cho Việt Nam.
- **Suggested visual:** Slide cảm ơn + liên hệ + nhắc lại 3 con số chủ chốt.
- **Speaker notes:** Chủ động nêu giới hạn cỡ mẫu Việt Nam (145) và cách khắc phục bằng ItViec. Sẵn sàng giải thích xử lý multi-select, winsorize lương, và vì sao net-change 2025 âm rộng (danh sách "muốn" ngắn hơn "đang dùng").
