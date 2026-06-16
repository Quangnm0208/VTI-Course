# QUESTION & ANSWER PREP
## Chuẩn bị câu hỏi phản biện cho buổi bảo vệ

> Tổng 15 câu hỏi điển hình + câu trả lời gợi ý, phân theo 4 nhóm tiêu chí
> đánh giá của đề bài (Technical / Analytical / Visualization / Recommendation).

---

## 🔧 NHÓM 1 — KỸ THUẬT (Technical)

**Q1: Vì sao chọn ItViec thay vì TopCV / VietnamWorks?**
> ItViec là cổng tuyển dụng IT chuyên biệt nhất ở Việt Nam, dữ liệu tập
> trung 100% vào ngành CNTT, mỗi job có tags kỹ năng rõ ràng — dễ trích
> xuất skill có cấu trúc. TopCV đa ngành, lẫn nhiều job ngoài IT.

**Q2: Cloudflare chặn được, em xử lý thế nào?**
> Em dùng 2 engine: `requests` cho tốc độ, `playwright` (Chromium headless)
> để vượt Cloudflare. Playwright có patch `navigator.webdriver=undefined`,
> đợi `networkidle`, phát hiện "Just a moment..." để đợi challenge. Khi
> 1 engine fail, tự động fallback engine còn lại.

**Q3: Idempotency là gì? Sao phải có?**
> Idempotency = chạy nhiều lần với cùng input → kết quả giống nhau. Em
> dùng khóa upsert `(scrape_date, source_url)` — nếu workflow vô tình
> chạy 2 lần trong ngày, dữ liệu KHÔNG bị nhân đôi. Quan trọng vì
> GitHub Actions có thể retry khi network lỗi.

**Q4: Atomic write tmp → fsync → rename để làm gì?**
> Để CSV không bị corrupt nếu process bị kill giữa lúc ghi (out of
> memory, timeout 10 phút). Pattern này được Linux đảm bảo atomic ở
> tầng filesystem qua syscall `rename()`.

**Q5: Tại sao chia thành 2 workflow (scrape + quality) thay vì 1?**
> Separation of concerns: scrape job có thể fail (network) nhưng không
> nên block quality check. Quality check chạy 30 phút sau scrape, kiểm
> tra 5 tiêu chí độc lập, có thể chạy lại nhiều lần mà không cần
> re-scrape. Mỗi job có concurrency group riêng tránh race condition.

---

## 📊 NHÓM 2 — PHÂN TÍCH (Analytical)

**Q6: 2 kỹ thuật thống kê em đã dùng là gì?**
> (1) **Tần suất & Tỷ lệ** — `COUNT(*) GROUP BY skill_name` để tính
> market share của mỗi kỹ năng.
> (2) **Tương quan đơn giản (demand/supply ratio)** —
> `#JD_mentions / #Dev_using` để tìm khoảng cách cung-cầu, xác định
> emerging skills.

**Q7: Em định nghĩa "emerging skill" như thế nào?**
> Em định nghĩa = skill có **Demand cao trong JD** nhưng **Supply thấp
> trong cộng đồng dev** (Stack Overflow). Cụ thể: demand/supply ratio
> > 2.0 và demand_jobs ≥ 10. Đây là chỉ báo "thiếu nhân sự" — cơ hội
> đào tạo lớn.

**Q8: Sao em chắc dữ liệu chính xác? Có bias không?**
> Có 2 bias em nhận thức rõ:
> (1) **Stack Overflow Survey** lệch về dev biết tiếng Anh, online —
> không đại diện toàn bộ dev VN.
> (2) **ItViec** lệch về job senior + công ty IT lớn — không phản ánh
> startup nhỏ.
> Để giảm bias em **ghép 2 nguồn** thay vì dùng 1. Kết luận em đưa ra
> dựa trên đồng thuận giữa 2 nguồn.

**Q9: Vì sao Python lại có Delta dương lớn nhất?**
> Vì AI/Data Science bùng nổ — Python là ngôn ngữ chính cho ML, data
> analysis. Dev hiện dùng JavaScript nhiều (web) nhưng muốn chuyển sang
> Python để theo AI. Delta = +25% chính là **làn sóng career switching**
> này.

**Q10: SQL không phải ngôn ngữ lập trình thuần, sao em xếp vào?**
> Em theo cách phân loại của Stack Overflow Survey — họ gộp SQL vào
> `language_worked_with`. Có thể tranh luận, nhưng từ góc độ thị trường
> tuyển dụng, SQL là yêu cầu bắt buộc với Backend & Data → việc xếp
> chung là hợp lý.

---

## 🎨 NHÓM 3 — TRỰC QUAN HÓA (Visualization)

**Q11: Vì sao em chọn Bar chart thay vì Pie chart cho Top Language?**
> Pie chart khó so sánh khi có > 5 mục. Top 10 ngôn ngữ cần xếp hạng
> rõ ràng → horizontal bar chart là chuẩn. Pie em dùng cho IDE & DB
> vì chỉ top 5 và muốn thể hiện thị phần (proportion).

**Q12: Vì sao có 2 slicer Country + Source?**
> Để người dùng so sánh chéo. Vd chọn Country=Vietnam + Source=ItViec
> để xem riêng thị trường VN, hoặc Source=StackOverflow để so với thế
> giới. Đáp ứng yêu cầu "2 bộ lọc tương tác" của đề.

**Q13: Dashboard có chạy real-time không?**
> Power BI desktop kết nối Direct Query tới SQLite thì có. Em build
> theo mode Import (refresh thủ công) để file `.pbix` portable. Pipeline
> tự động đã đảm bảo CSV cập nhật mỗi ngày → đủ "near real-time".

---

## 💡 NHÓM 4 — KIẾN NGHỊ (Recommendation)

**Q14: Kiến nghị "mở khóa Cloud DevOps" có khả thi không?**
> Hoàn toàn khả thi. AWS, Docker đều có free tier cho học viên thực
> hành. VTI có thể partner với AWS Training (có chương trình
> AWS Educate miễn phí). Em đã tính: 1 khóa Docker 8 tuần + AWS CP 12
> tuần = đáp ứng được Critical Gap em phát hiện.

**Q15: Nếu em là CEO VTI, em ưu tiên kiến nghị nào trước?**
> Em ưu tiên **kiến nghị #3 (pipeline tự động)** trước, dù nó
> không "sexy" nhất. Lý do: 2 kiến nghị còn lại sẽ lỗi thời sau 1-2
> năm, nhưng **năng lực phân tích liên tục** sẽ giúp VTI tự ra quyết
> định cho mọi xu hướng tương lai. Đầu tư hạ tầng dữ liệu = đầu tư
> dài hạn.

---

## 🔥 CÂU HỎI KHÓ (Bonus)

**Q-bonus 1: Nếu ItViec ban IP của em vĩnh viễn?**
> 3 phương án backup: (1) thay nguồn — TopCV / LinkedIn Jobs;
> (2) self-hosted runner ở VN với IP nội địa; (3) dùng dịch vụ proxy
> rotating như Bright Data. Em đã thiết kế kiến trúc fetcher tách rời
> nên đổi nguồn chỉ cần thêm 1 class mới.

**Q-bonus 2: Pipeline em có thể scale lên 10 nguồn không?**
> Có. Em đã abstract layer fetcher (như reference ETF có
> source_cafef/yfinance/vnstock). Mỗi nguồn 1 file, thêm vào
> `FETCHERS` dict. CSV schema dùng chung → upsert vẫn hoạt động.
> Bottleneck duy nhất là GitHub Actions timeout 6h/job — đủ cho ~50
> nguồn.

**Q-bonus 3: Bảo mật secrets thế nào?**
> Em không hardcode API key trong code. GitHub Secrets được dùng cho
> các giá trị nhạy cảm (Telegram bot token nếu có alert). `.gitignore`
> loại bỏ file `.env` local. Repo public an toàn.
