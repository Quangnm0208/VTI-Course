# Kịch bản bảo vệ đồ án (15 phút) — Một ngày của Data Analyst: Phân tích xu hướng kỹ năng IT

*Tổng thời lượng: 15 phút. Số liệu từ Stack Overflow Developer Survey 2025: 49.191 lập trình viên, 177 quốc gia.*

---

## [1 phút] Bối cảnh

Kính chào hội đồng. Đồ án của em trả lời một câu hỏi kinh doanh cụ thể của VTI Academy: **nên ưu tiên đào tạo kỹ năng IT nào để bám sát nhu cầu tuyển dụng thực tế?** Đào tạo sai kỹ năng vừa lãng phí ngân sách xây khóa học, vừa khiến học viên khó có việc. Em phân tích khảo sát mới nhất — 49.191 lập trình viên trên 177 quốc gia — kết hợp dữ liệu nhu cầu công nghệ và tuyển dụng, để khuyến nghị ngôn ngữ, cơ sở dữ liệu và vai trò nghề nghiệp nên ưu tiên.

## [2 phút] Dữ liệu & Phương pháp

Em dùng ba nguồn bổ trợ nhau. **Thứ nhất, Stack Overflow Developer Survey 2025** — 49.191 lập trình viên, 177 quốc gia — làm benchmark toàn cầu. **Thứ hai, GitHub REST API** (7.600 repo) đo độ phổ biến công nghệ trên mã nguồn mở. **Thứ ba, ItViec job postings**, scrape bằng Playwright, làm proxy nhu cầu tuyển dụng Việt Nam; ItViec ẩn lương sau đăng nhập nên trường lương được đánh dấu `login_required` thay vì ước đoán.

Về chân dung mẫu: kinh nghiệm trung vị 10 năm, 68,6% có việc làm chính thức, lương trung vị $75.320/năm, trung bình mỗi người dùng 4,0 ngôn ngữ. Em dùng ba kỹ thuật thống kê: **(1) đếm tần suất và tỷ lệ phần trăm**; **(2) growth-gap = số người muốn dùng năm tới trừ số người đang dùng**; và **(3) lương trung vị có rào chắn cỡ mẫu, winsorize tại $300k** vì lương tự khai có ngoại lai.

## [3 phút] Làm sạch dữ liệu & SQL

Thách thức làm sạch lớn nhất là các **cột multi-select**: ngôn ngữ, database được lưu dưới dạng chuỗi nối bằng dấu chấm phẩy, ví dụ `Python;SQL;JavaScript`. Em **tách theo dấu `;` thành định dạng long** — mỗi dòng là một cặp (người trả lời, kỹ năng). Trong quá trình đó em **loại bỏ giá trị NaN** để không đếm ô trống, và **khử trùng lặp trong cùng một người** để một người chỉ được tính một lần cho mỗi kỹ năng.

Sau khi có bảng long, phép đếm trở thành SQL chuẩn: `GROUP BY language` rồi `COUNT(DISTINCT respondent_id)` cho cột "đang dùng" và cột "muốn dùng năm tới", sau đó `JOIN` hai bảng để tính growth-gap. Với lương, em `JOIN` bảng kỹ năng với lương cá nhân, lọc bỏ giá trị vượt $300k (winsorize) rồi tính trung vị theo từng ngôn ngữ, đồng thời luôn giữ cột `COUNT` cỡ mẫu để không kết luận trên nhóm quá nhỏ. Cách này giúp con số minh bạch, tái lập được và kiểm chứng được.

*Một lưu ý phương pháp quan trọng:* trong khảo sát 2025, danh sách "muốn dùng" trung bình ngắn hơn "đang dùng", nên **net-change phần lớn âm**. Vì vậy em đọc theo hai trục: **độ phổ biến tuyệt đối** (ai được muốn nhiều nhất) và **đà tăng** (kỹ năng nào có net dương — tín hiệu mạnh hiếm hoi).

## [5 phút] Phát hiện chính

**Thứ nhất — Python và SQL là nền tảng được mong muốn nhất.** Python dẫn đầu nhu cầu năm tới với 12.419 lượt, SQL 11.257, rồi HTML/CSS, JavaScript, TypeScript đều quanh 10.000–10.600. *Ý nghĩa cho VTI:* lộ trình cốt lõi phải xoay quanh Python, SQL và bộ Web — đây là nhóm vừa phổ biến vừa được mong muốn nhất.

**Thứ hai — Rust là ngôi sao tăng trưởng.** Rust được 9.262 lập trình viên muốn dùng — chiếm 18,8% thị trường — và **tăng +96%** so với số đang dùng: vừa nhu cầu lớn, vừa đà tăng mạnh. Theo sau là Go +42%, Zig +255% và Elixir +115% (nền nhỏ hơn). *Ý nghĩa:* Rust và Go xứng đáng thành elective chính thức cho học viên đã có nền, không chỉ là khóa thử nghiệm.

**Thứ ba — PostgreSQL thống trị cơ sở dữ liệu.** PostgreSQL vừa được dùng nhiều nhất vừa được muốn nhất (11.863), và giảm nhẹ nhất nhóm DB (−18%, xếp "Stable"); Redis ổn định. Ngược lại MySQL giảm −52%, MS SQL Server −51%, MongoDB −30%. *Ý nghĩa:* nên dạy **PostgreSQL làm chuẩn SQL** và thêm Redis cho phần caching, thay vì MySQL/SQL Server thuần.

**Thứ tư — IDE (lưu ý trung thực).** Khảo sát 2025 đã **bỏ câu hỏi về IDE**, nên em lấy số liệu IDE từ kỳ gần nhất có hỏi và ghi chú rõ trên dashboard: Visual Studio Code vẫn thống trị (~55%). Em nêu rõ giới hạn này thay vì trộn lẫn dữ liệu khác năm mà không chú thích.

**Thứ năm — ưu tiên theo vai trò và lương.** Full-stack là nhóm lớn nhất với 12.351 lập trình viên — Ưu tiên 1; Back-end 6.453 người, lương trung vị $78.616 — Ưu tiên 2. Nhóm lương cao nhất là Product/BA $122k, DevOps $87k, Data Scientist/ML $81k. *Ý nghĩa:* dồn năng lực vào lộ trình Full-stack và Back-end vì quy mô nhu cầu lớn nhất; DevOps, Data Science, Product/BA là các khóa cao cấp biên lợi nhuận tốt.

## [2 phút] Dashboard

Toàn bộ phát hiện được đóng gói trong một **dashboard Power BI tương tác 4 trang**: Tổng quan, Cung–cầu kỹ năng, Việt Nam (ItViec), Khuyến nghị. Trang tổng quan có KPI: 49.191 lập trình viên, lương trung vị $75.320, phân bổ quốc gia (Mỹ 14,7%, Đức 6,1%, Ấn Độ 5,2%). Các trang sau trực quan hóa growth-gap ngôn ngữ và database, bảng lương theo ngôn ngữ — nhóm chuyên sâu như Ruby $103k, Erlang $100k, Elixir $99k trả cao nhất — và bảng ưu tiên vai trò. Điểm mạnh là người dùng **tự lọc theo tín hiệu, vai trò hoặc lương** để ra quyết định, và có thể tái sử dụng mỗi mùa tuyển sinh khi dữ liệu cập nhật.

## [2 phút] Khuyến nghị

Em đề xuất bốn hành động. **Một**, lộ trình cốt lõi quanh Python, SQL, PostgreSQL, Git và JavaScript/TypeScript — đúng nhóm được mong muốn nhất. **Hai**, mở elective đón đầu cho Rust và Go (nhu cầu lớn, đà tăng, lương tốt), thêm Elixir/Zig cho lớp nâng cao. **Ba**, xây track cao cấp DevOps, Data Science/ML và Product/BA — đây là nhóm lương thị trường cao nhất, định giá premium được. **Bốn**, mọi quyết định cho thị trường Việt Nam phải được xác thực bằng ItViec, không suy diễn từ 145 phản hồi khảo sát. Em xin nhấn mạnh: Stack Overflow là benchmark toàn cầu, ItViec là tín hiệu địa phương. Em xin cảm ơn hội đồng và sẵn sàng trả lời câu hỏi.

---

## Q&A Preparation — Chuẩn bị câu hỏi phản biện

**1. Vì sao chọn các nguồn dữ liệu này?**
Ba nguồn bù đắp điểm yếu của nhau. Stack Overflow 2025 cho quy mô lớn và độ tin cậy (49.191 người, 177 quốc gia) nhưng nghiêng về phương Tây và ít dữ liệu Việt Nam. GitHub API đo độ phổ biến thực tế của công nghệ trên mã nguồn mở. ItViec bù khoảng trống địa phương: nó phản ánh nhu cầu tuyển dụng thực tế tại Việt Nam. Kết hợp: benchmark toàn cầu + tín hiệu mã nguồn mở + tín hiệu tuyển dụng nội địa.

**2. Dữ liệu có đại diện cho Việt Nam không?**
Khảo sát thì **chưa đủ** — Việt Nam có 145 phản hồi (đã tăng từ 12 ở kỳ trước nhưng vẫn nhỏ). Em xử lý minh bạch: coi Stack Overflow là **benchmark xu hướng công nghệ toàn cầu** (xu hướng ngôn ngữ/database mang tính quốc tế nên vẫn hữu ích), còn đặc thù Việt Nam thì **xác thực bằng ItViec**. Em không over-conclude về Việt Nam từ 145 mẫu và nêu rõ giới hạn này trong báo cáo.

**3. Vì sao dùng thống kê tần suất/phần trăm/growth-gap?**
Câu hỏi kinh doanh là "nên ưu tiên kỹ năng nào", tức so sánh độ phổ biến và xu hướng — đếm tần suất và tỷ lệ phần trăm trả lời trực tiếp, dễ hiểu với người ra quyết định. Growth-gap (muốn dùng trừ đang dùng) là chỉ số dẫn dắt: nó cho biết kỹ năng nào **sẽ** lên/xuống, đúng nhu cầu lập kế hoạch đào tạo cho năm tới. Em không cần mô hình phức tạp hơn vì bài toán là mô tả và ưu tiên, không phải dự báo nhân quả.

**4. Net-change phần lớn âm thì đọc thế nào?**
Đây là đặc điểm của khảo sát 2025: trung bình mỗi người liệt kê ít kỹ năng "muốn dùng" hơn "đang dùng", nên hầu hết kỹ năng có net âm. Vì vậy em đọc theo hai trục: **độ phổ biến tuyệt đối** (Python, SQL được muốn nhiều nhất) và **đà tăng tương đối** — kỹ năng nào net **dương** giữa bối cảnh đó là tín hiệu mạnh đặc biệt, chính là Rust, Go, Zig, Elixir. Em không kết luận "tất cả ngôn ngữ đều giảm" — đó là hiểu sai bản chất dữ liệu.

**5. Xử lý cột multi-select thế nào?**
Các cột này lưu nhiều lựa chọn nối bằng dấu chấm phẩy. Em **tách theo `;` thành định dạng long**, mỗi dòng một cặp (người, kỹ năng). Ba nguyên tắc: **không đếm NaN** (tránh thổi phồng mẫu số), **khử trùng lặp trong cùng một người** (một người tính một lần cho mỗi kỹ năng), và giữ `respondent_id` để join ngược về lương/vai trò. Sau đó phép đếm chỉ còn là `GROUP BY` + `COUNT(DISTINCT respondent_id)`.

**6. Vì sao khuyến nghị này đúng cho VTI Academy?**
Vì nó gắn trực tiếp với lợi ích Academy: tập trung Python/SQL/PostgreSQL và lộ trình Full-stack/Back-end nghĩa là đào tạo đúng nơi nhu cầu lớn nhất (Full-stack 12.351 dev) và được mong muốn nhất — học viên dễ có việc, tỷ lệ tuyển sinh và uy tín tăng. Elective Rust/Go và track DevOps/Data Science tận dụng mức lương cao để định giá premium, tăng doanh thu. Nguyên tắc xác thực bằng ItViec giảm rủi ro đào tạo lệch nhu cầu Việt Nam — bảo vệ chính ngân sách của Academy.

**7. Nếu có thêm thời gian, em sẽ cải thiện gì?**
Bốn việc: **(a)** mở rộng dữ liệu Việt Nam bằng cách scrape thêm TopCV, VietnamWorks bên cạnh ItViec để có cỡ mẫu địa phương đủ lớn; **(b)** giải quyết lương `login_required` của ItViec bằng nguồn lương khác hoặc đăng nhập hợp lệ; **(c)** thêm phân tích chuỗi thời gian để xác nhận xu hướng growth-gap không phải nhiễu một năm; **(d)** đối chiếu nguồn cung khóa học hiện tại của VTI với cầu để định lượng khoảng cách cung–cầu cho từng kỹ năng.
