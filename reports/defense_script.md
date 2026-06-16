# Kịch bản bảo vệ đồ án (15 phút) — Một ngày của Data Analyst: Phân tích xu hướng kỹ năng IT

*Tổng thời lượng: 15 phút. Số liệu từ Stack Overflow Developer Survey: 11.552 lập trình viên, 135 quốc gia.*

---

## [1 phút] Bối cảnh

Kính chào hội đồng. Đồ án của em trả lời một câu hỏi kinh doanh cụ thể của VTI Academy: **nên ưu tiên đào tạo kỹ năng IT nào để bám sát nhu cầu tuyển dụng thực tế?** Đào tạo sai kỹ năng vừa lãng phí ngân sách xây khóa học, vừa khiến học viên khó có việc. Em phân tích dữ liệu khảo sát 11.552 lập trình viên trên 135 quốc gia, kết hợp dữ liệu tuyển dụng Việt Nam, để đưa ra khuyến nghị về ngôn ngữ, cơ sở dữ liệu, công cụ và vai trò nghề nghiệp nên ưu tiên.

## [2 phút] Dữ liệu & Phương pháp

Em dùng ba nguồn bổ trợ nhau. **Thứ nhất, Stack Overflow Developer Survey** — file CSV 90 cột, 11.552 lập trình viên, 135 quốc gia — làm benchmark toàn cầu. **Thứ hai, ItViec job postings**, scrape hằng ngày bằng Playwright, làm proxy cho nhu cầu tuyển dụng tại Việt Nam; lưu ý ItViec ẩn lương sau đăng nhập nên trường lương được đánh dấu `login_required`, em không bịa con số. **Thứ ba, các cổng đào tạo** phản ánh nguồn cung khóa học hiện có (tùy chọn).

Về chân dung mẫu: 96,2% làm full-time, kinh nghiệm coding chuyên nghiệp trung vị 5 năm, lương trung vị $57.844/năm, trung bình mỗi người dùng 5,2 ngôn ngữ và muốn học thêm 4,9. Em dùng ba kỹ thuật thống kê: **(1) đếm tần suất và tỷ lệ phần trăm**; **(2) growth-gap = số người muốn dùng năm tới trừ số người đang dùng**; và **(3) lương trung vị có rào chắn cỡ mẫu, winsorize tại $300k** vì lương tự khai có ngoại lai.

## [3 phút] Làm sạch dữ liệu & SQL

Thách thức làm sạch lớn nhất là các **cột multi-select**: ngôn ngữ, database, IDE được lưu dưới dạng chuỗi nối bằng dấu chấm phẩy, ví dụ `Python;SQL;JavaScript`. Em **tách theo dấu `;` thành định dạng long** — mỗi dòng là một cặp (người trả lời, kỹ năng). Trong quá trình đó em **loại bỏ giá trị NaN** để không đếm ô trống, và **khử trùng lặp trong cùng một người** để một người chỉ được tính một lần cho mỗi kỹ năng.

Sau khi có bảng long, phép đếm trở thành SQL chuẩn: `GROUP BY language` rồi `COUNT(DISTINCT respondent_id)` cho cột "đang dùng" và cột "muốn dùng năm tới", sau đó `JOIN` hai bảng để tính growth-gap. Với lương, em `JOIN` bảng kỹ năng với lương cá nhân, lọc bỏ giá trị vượt $300k (winsorize) rồi tính `MEDIAN` theo từng ngôn ngữ, đồng thời luôn giữ cột `COUNT` cỡ mẫu để không kết luận trên nhóm quá nhỏ. Cách này giúp con số minh bạch, có thể tái lập và kiểm chứng.

## [5 phút] Phát hiện chính

**Thứ nhất — Python và TypeScript là tương lai gần.** Python tăng +15,1% (từ 4.611 lên 5.309 người muốn dùng), TypeScript tăng +26,6% (3.269 lên 4.140). Ngược lại JavaScript giảm −23,7%, Java −34,4%, và PHP giảm tới −50%. *Ý nghĩa cho VTI:* lộ trình cốt lõi nên xoay quanh Python và TypeScript thay vì PHP hay Java thuần. *Khuyến nghị:* tái cấu trúc khóa lập trình nền tảng theo hai ngôn ngữ này.

**Thứ hai — nhóm ngôn ngữ tăng trưởng nóng nhưng nền còn nhỏ.** Rust +369,5%, WebAssembly +941,9%, Kotlin +152,9%, Go +148,3%. Các con số phần trăm lớn vì xuất phát điểm thấp (Rust chỉ 328 người đang dùng). *Ý nghĩa:* đây là tín hiệu cho khóa nâng cao, không phải lộ trình cơ bản. *Khuyến nghị:* mở các elective ngắn cho học viên đã có nền tảng.

**Thứ ba — cơ sở dữ liệu dịch chuyển rõ rệt.** PostgreSQL dẫn đầu nhu cầu mong muốn với 4.386 người (+5,6%), Redis +33,5%, MongoDB +21,1%, Elasticsearch +46,4%. Ngược lại MySQL giảm −40%, Oracle −50%, MS SQL Server −34,1%. *Ý nghĩa:* nên dạy PostgreSQL làm chuẩn SQL và bổ sung NoSQL (MongoDB, Redis), thay vì MySQL/Oracle thuần. *Khuyến nghị:* cập nhật học phần database.

**Thứ tư — môi trường phát triển đã hội tụ.** Visual Studio Code thống trị khoảng 55% gần như mọi vai trò; IPython/Jupyter đứng đầu nhóm Data Scientist (390 người); Vim là công cụ số 2 của DevOps. *Ý nghĩa:* chuẩn hóa thực hành quanh VS Code, dùng Jupyter cho học phần dữ liệu. *Khuyến nghị:* thống nhất môi trường thực hành để giảm ma sát cho học viên.

**Thứ năm — ưu tiên tuyển sinh theo vai trò.** Full-stack có 6.928 lập trình viên, lương trung vị $59.000 — Ưu tiên 1; Back-end 6.290 người, $56.715 — Ưu tiên 2. DevOps tuy ít người (1.639) nhưng lương cao nhất, $71.036. *Ý nghĩa:* dồn năng lực vào lộ trình Full-stack và Back-end vì quy mô nhu cầu lớn nhất; DevOps là khóa cao cấp biên lợi nhuận tốt. *Khuyến nghị:* phân bổ ngân sách đào tạo theo ba mức ưu tiên này.

## [2 phút] Dashboard

Toàn bộ phát hiện được đóng gói trong một **dashboard Power BI tương tác**. Trang tổng quan có các thẻ KPI: 11.552 lập trình viên, lương trung vị $57.844, phân bổ theo quốc gia (Mỹ 27,5%, Ấn Độ 7,9%, Anh 7,3%). Các trang tiếp theo trực quan hóa growth-gap ngôn ngữ và database, bảng lương trung vị theo ngôn ngữ — từ Clojure $93.404, Go $80.000, Python $64.000 đến PHP $43.296 — và bảng ưu tiên vai trò. Điểm mạnh là người dùng có thể **tự lọc theo vai trò, kỹ năng hoặc mức lương** để ra quyết định, thay vì đọc một báo cáo tĩnh. Dashboard này có thể tái sử dụng mỗi mùa tuyển sinh khi dữ liệu được cập nhật.

## [2 phút] Khuyến nghị

Em đề xuất ba hành động. **Một**, tái cấu trúc lộ trình cốt lõi quanh Python, TypeScript và PostgreSQL, giảm dần PHP và Java thuần — bám đúng nhu cầu tăng trưởng và hai vai trò Full-stack, Back-end ưu tiên cao nhất. **Hai**, mở các khóa elective ngắn cho kỹ năng tăng trưởng nóng (Go, Rust, Kotlin, MongoDB, Redis, DevOps) hướng đến học viên đã có nền, và định giá premium nhờ mức lương cao của các kỹ năng này. **Ba**, mọi quyết định cho thị trường Việt Nam phải được xác thực bằng dữ liệu ItViec, không suy diễn từ 12 phản hồi khảo sát của Việt Nam. Em xin nhấn mạnh giới hạn này một cách chủ động: Stack Overflow là benchmark toàn cầu, ItViec là tín hiệu địa phương. Em xin cảm ơn hội đồng và sẵn sàng trả lời câu hỏi.

---

## Q&A Preparation — Chuẩn bị câu hỏi phản biện

**1. Vì sao chọn các nguồn dữ liệu này?**
Ba nguồn bù đắp điểm yếu của nhau. Stack Overflow cho quy mô lớn và độ tin cậy (11.552 người, 135 quốc gia) nhưng nghiêng về phương Tây và ít dữ liệu Việt Nam. ItViec bù đúng khoảng trống đó: nó phản ánh nhu cầu tuyển dụng thực tế tại Việt Nam, scrape hằng ngày nên cập nhật. Cổng đào tạo cho biết nguồn cung khóa học hiện có để phát hiện khoảng cách cung–cầu. Kết hợp lại: benchmark toàn cầu + tín hiệu địa phương + nguồn cung.

**2. Dữ liệu có đại diện cho Việt Nam không?**
Khảo sát thì **không** — Việt Nam chỉ có 12 phản hồi, quá nhỏ để kết luận riêng. Em xử lý minh bạch: coi Stack Overflow là **benchmark xu hướng công nghệ toàn cầu** (xu hướng ngôn ngữ/database mang tính quốc tế nên vẫn hữu ích), còn mọi đặc thù Việt Nam — kỹ năng được tuyển nhiều, mức độ phổ biến — em **xác thực bằng ItViec**. Em không over-conclude về Việt Nam từ 12 mẫu, và nêu rõ giới hạn này ngay trong báo cáo.

**3. Vì sao dùng thống kê tần suất/phần trăm/growth-gap?**
Câu hỏi kinh doanh là "nên ưu tiên kỹ năng nào", tức là so sánh độ phổ biến và xu hướng — đếm tần suất và tỷ lệ phần trăm trả lời trực tiếp câu hỏi đó, dễ hiểu với người ra quyết định không chuyên kỹ thuật. Growth-gap (muốn dùng trừ đang dùng) là chỉ số dẫn dắt (leading indicator): nó cho biết kỹ năng nào **sẽ** lên/xuống chứ không chỉ trạng thái hiện tại — đúng nhu cầu lập kế hoạch đào tạo cho năm tới. Em không cần mô hình phức tạp hơn vì bài toán là mô tả và ưu tiên, không phải dự báo nhân quả.

**4. Xử lý cột multi-select thế nào?**
Các cột này lưu nhiều lựa chọn nối bằng dấu chấm phẩy, ví dụ `Python;SQL;JavaScript`. Em **tách theo `;` thành định dạng long**, mỗi dòng một cặp (người, kỹ năng). Ba nguyên tắc: **không đếm NaN** (bỏ ô trống để tránh thổi phồng mẫu số), **khử trùng lặp trong cùng một người** (một người chỉ tính một lần cho mỗi kỹ năng, tránh đếm lặp), và giữ `respondent_id` để có thể join ngược về lương/vai trò. Sau đó phép đếm chỉ còn là `GROUP BY` + `COUNT(DISTINCT respondent_id)`.

**5. Vì sao khuyến nghị này đúng cho VTI Academy?**
Vì nó gắn trực tiếp với lợi ích của Academy: tập trung vào Python/TypeScript/PostgreSQL và lộ trình Full-stack/Back-end nghĩa là đào tạo đúng nơi nhu cầu lớn nhất (Full-stack 6.928 dev) và đang tăng — học viên dễ có việc, tỷ lệ tuyển sinh và uy tín tăng. Các elective kỹ năng nóng (Go, Rust, DevOps) tận dụng mức lương cao ($71k cho DevOps) để định giá premium, tăng doanh thu. Đồng thời nguyên tắc xác thực bằng ItViec giảm rủi ro đào tạo lệch nhu cầu Việt Nam — bảo vệ chính ngân sách của Academy.

**6. Nếu có thêm thời gian, em sẽ cải thiện gì?**
Bốn việc: **(a)** mở rộng dữ liệu Việt Nam bằng cách scrape thêm TopCV, VietnamWorks bên cạnh ItViec để có cỡ mẫu địa phương đủ lớn; **(b)** giải quyết vấn đề lương `login_required` của ItViec bằng nguồn lương khác hoặc đăng nhập hợp lệ; **(c)** thêm phân tích theo thời gian (time-series) để xác nhận xu hướng growth-gap không phải nhiễu một năm; **(d)** đối chiếu nguồn cung khóa học hiện tại của VTI với cầu để định lượng chính xác khoảng cách cung–cầu cho từng kỹ năng.
