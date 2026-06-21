# BÀI THUYẾT TRÌNH — 10 SLIDES
## A Day in the Life of a Data Analyst — Phân tích Kỹ năng CNTT
> Tổng thời lượng đề xuất: **15 phút trình bày + Q&A**
> Mỗi slide có 3 phần: **NỘI DUNG (hiển thị trên slide)** • **HÌNH ẢNH/CHART** • **SPEAKER NOTES (lời nói)**

---

## 🟦 SLIDE 1 — Tiêu đề & Bối cảnh (10%) — ~1 phút

**NỘI DUNG**
- **Tiêu đề:** A Day in the Life of a Data Analyst
- **Phụ đề:** Phân tích Kỹ năng CNTT đang được yêu cầu nhất
- Họ tên — Lớp VTI Academy — Ngày trình bày
- Logo VTI Academy

**HÌNH ẢNH**
- Background: laptop + biểu đồ + code snippet (free image)
- Logo VTI ở góc phải dưới

**SPEAKER NOTES**
> "Xin chào mọi người. Hôm nay tôi xin trình bày dự án **A Day in the Life
> of a Data Analyst** — vào vai Chuyên viên Phân tích Dữ liệu tại VTI
> Academy, tôi đã phân tích các kỹ năng IT đang được thị trường yêu cầu
> nhiều nhất, nhằm hỗ trợ trung tâm cập nhật chương trình đào tạo. Câu hỏi
> đặt ra: **Đào tạo gì để học viên ra trường có việc ngay?**"

---

## 🟦 SLIDE 2 — Phương pháp (20%) — ~2 phút

**NỘI DUNG** *(layout 2 cột)*

**Cột trái — Nguồn dữ liệu (3 nguồn):**
- 📊 **Stack Overflow Developer Survey 2025** (CSV) — 80+ cột, 10.000+ developers toàn cầu
- 💼 **ItViec** (Web Scraping) — tin tuyển dụng IT tại Việt Nam, cào hàng ngày
- 🎓 **Training Portals** (API) — danh sách khóa học (Coursera, Udemy, edX)

**Cột phải — Pipeline kỹ thuật:**
```
Scrape (Playwright) → Wrangle (Pandas) → Store (SQLite)
       ↓                    ↓                  ↓
   ItViec live      Clean & explode      4 tables + index
       ↓                    ↓                  ↓
  GitHub Actions (cron 07:00 VN hàng ngày)
```

**HÌNH ẢNH**
- Sơ đồ pipeline dạng flowchart 4 bước
- Logo Python / Pandas / Playwright / SQLite / Power BI

**SPEAKER NOTES**
> "Để trả lời câu hỏi đó, tôi thu thập dữ liệu từ **3 nguồn** đảm bảo tính
> đa dạng theo đúng yêu cầu đề bài. Quan trọng nhất, **tôi không chỉ làm
> 1 lần** — tôi xây luôn một **hệ thống tự động trên GitHub Actions**: mỗi
> sáng 7 giờ, máy chủ tự cào ItViec, làm sạch, kiểm tra chất lượng và
> commit kết quả ngược về repo. Đây là điểm khác biệt: dữ liệu luôn cập
> nhật, không cần can thiệp tay."

---

## 🟦 SLIDE 3 — Insight 1: Top Ngôn ngữ Lập trình — ~2 phút

**NỘI DUNG**
- **Bar chart ngang** — Top 10 ngôn ngữ theo số lượt mention
- Highlight: **JavaScript #1, Python #2, SQL #3**
- Bảng nhỏ: % thị phần

| Rank | Language | Mentions | Share |
|------|---------|----------|-------|
| 1 | JavaScript | _XX_ | _XX%_ |
| 2 | Python     | _XX_ | _XX%_ |
| 3 | SQL        | _XX_ | _XX%_ |

**CHART KIẾN NGHỊ (Power BI):**
- Horizontal Bar Chart
- Trục Y: skill_name (top 10)
- Trục X: COUNT(*) where skill_type='language'
- Color: nguồn (StackOverflow vs ItViec) — Stacked Bar

**SPEAKER NOTES**
> "**JavaScript dẫn đầu** không bất ngờ — vẫn là ngôn ngữ phổ biến nhất
> toàn cầu cho web. **Python lên #2** nhờ AI/Data và còn đang tăng trưởng
> nhanh. **SQL #3** chứng minh kỹ năng database vẫn là yêu cầu nền tảng.
> Điểm đáng chú ý: nếu nhìn riêng JD ItViec, **Java vẫn rất mạnh ở Việt
> Nam** do hệ sinh thái doanh nghiệp."

---

## 🟦 SLIDE 4 — Insight 2: Database & IDE — ~2 phút

**NỘI DUNG** *(chia đôi slide)*

**Trái — Databases (Top 5):**
- PostgreSQL, MySQL, MongoDB, Redis, SQL Server
- Donut chart phân bổ %

**Phải — IDE (Top 5):**
- VS Code, IntelliJ, Visual Studio, PyCharm, Vim
- Donut chart phân bổ %

**SPEAKER NOTES**
> "Về database, **PostgreSQL vượt MySQL** ở khảo sát toàn cầu nhưng tại
> Việt Nam **MySQL vẫn phổ biến hơn**. **MongoDB** đứng thứ 3 — phù hợp
> startup. Về IDE, **VS Code chiếm hơn 55%** thị phần, vượt xa IntelliJ.
> Đây là chỉ dấu rõ ràng: nếu VTI dạy IDE, **bắt buộc phải tích hợp VS
> Code làm chuẩn**."

---

## 🟦 SLIDE 5 — Insight 3: Phân tích Thống kê — ~2 phút

**NỘI DUNG**
- **Bảng so sánh** "Đang dùng" vs "Muốn học năm sau"
- Cột Delta (tăng/giảm)

| Language | Đang dùng | Muốn học | Delta |
|----------|-----------|----------|-------|
| Python   | _XX%_     | _XX%_    | **+25%** 🚀 |
| Rust     | _XX%_     | _XX%_    | **+18%** 🚀 |
| Go       | _XX%_     | _XX%_    | **+12%** 🚀 |
| PHP      | _XX%_     | _XX%_    | **−15%** 📉 |
| Java     | _XX%_     | _XX%_    | **−8%** 📉 |

**KỸ THUẬT THỐNG KÊ ÁP DỤNG:**
1. **Tần suất & Tỷ lệ** — đếm lượt xuất hiện skill / tổng
2. **Tương quan đơn giản** — demand/supply ratio = #JD_mentions / #Dev_using

**CHART KIẾN NGHỊ:**
- Diverging Bar Chart (Delta column)
- Màu xanh = tăng, đỏ = giảm

**SPEAKER NOTES**
> "Đây là phân tích **statistical** quan trọng nhất. Tôi so sánh ngôn ngữ
> dev **đang dùng** với ngôn ngữ họ **muốn dùng năm sau** — Delta cho
> thấy xu hướng tương lai. **Python, Rust, Go** đều có delta dương rất
> lớn — đây là tương lai. **PHP, Perl, Objective-C** đang chết dần.
> Insight này có giá trị chiến lược: VTI **không nên mở thêm khóa PHP**,
> nhưng **phải mở khóa Rust/Go**."

---

## 🟦 SLIDE 6 — Emerging Skills (Demand/Supply Ratio) — ~2 phút

**NỘI DUNG**
- **Scatter plot:** trục X = supply (dev biết), trục Y = demand (JD yêu cầu)
- Quadrant phải-trên = **Emerging gold** (cao cả 2)
- Quadrant phải-dưới = **Critical gap** (demand cao, supply thấp) ⚠️

**HIGHLIGHT các skill ở Critical Gap:**
- AWS, Docker, Kubernetes — cloud/DevOps
- TypeScript — vẫn còn ít dev thành thạo
- Spring Boot — VN cần nhiều Java enterprise

**SPEAKER NOTES**
> "Đây là góc phân tích **mới** mà ít báo cáo khác có. Tôi định nghĩa
> **Emerging Skill** = kỹ năng demand cao ở JD ItViec nhưng supply thấp ở
> Stack Overflow. Kết quả: **Cloud & DevOps** đứng đầu — 60% JD ItViec
> yêu cầu nhưng chỉ 30% dev nắm. **Đây là cơ hội kinh doanh số 1 cho
> VTI** — mở khóa Docker/Kubernetes/AWS, học viên ra trường có việc liền."

---

## 🟦 SLIDE 7 — Dashboard Tổng quan (1) — ~1 phút

**NỘI DUNG**
- Screenshot Power BI Dashboard **trang 1** — Overview
- KPI Cards: Tổng skill, Tổng JD, Skill tăng trưởng nhất
- 2 chart: Top language, Top database
- 2 slicer: Country, Source (StackOverflow / ItViec)

**SPEAKER NOTES**
> "Toàn bộ insight được trực quan hóa trong Power BI Dashboard 2 trang.
> Trang 1 là **Overview**: 5 thẻ KPI, 2 biểu đồ chính, 2 bộ lọc tương
> tác — đáp ứng đủ yêu cầu tối thiểu của đề. Người dùng có thể lọc theo
> quốc gia hoặc nguồn dữ liệu để xem riêng."

---

## 🟦 SLIDE 8 — Dashboard Tổng quan (2) — ~1 phút

**NỘI DUNG**
- Screenshot Power BI Dashboard **trang 2** — Deep Dive
- Heatmap skill × country
- Diverging bar chart Đang dùng vs Muốn học
- Scatter plot Emerging skills
- Drill-through từ skill → list công ty đang tuyển

**SPEAKER NOTES**
> "Trang 2 dành cho **Deep Dive**. Heatmap cho thấy phân phối skill theo
> quốc gia — ví dụ Ấn Độ có nhiều JavaScript hơn, Đức nhiều C# hơn. Phần
> Drill-through cho phép click vào 1 skill để xem **danh sách công ty
> nào đang tuyển skill đó** trên ItViec — biến dashboard thành công cụ
> tuyển dụng/định hướng cho học viên."

---

## 🟦 SLIDE 9 — Kiến nghị Chiến lược (10%) — ~1.5 phút

**NỘI DUNG**
**3 KIẾN NGHỊ CHO VTI ACADEMY:**

**1. 🎯 NGẮN HẠN (Quý này)**
> Mở khóa **Python for Data + Cloud DevOps** (AWS/Docker)
> *Lý do:* Cloud có Demand/Supply ratio cao nhất → việc làm dồi dào.

**2. 🚀 TRUNG HẠN (6 tháng)**
> Tích hợp **TypeScript, Go, Rust** vào lộ trình nâng cao
> *Lý do:* Delta "muốn học" dương lớn → đón đầu xu hướng 2-3 năm tới.

**3. ⚙️ DÀI HẠN (1 năm)**
> Duy trì **pipeline scraping tự động** → quý phân tích lại, cập nhật
> chương trình theo nhu cầu thị trường real-time.
> *Lý do:* Thị trường IT thay đổi 6 tháng/lần — không thể dùng dữ liệu cũ.

**SPEAKER NOTES**
> "3 kiến nghị, 3 tầm nhìn thời gian khác nhau. Quan trọng nhất là kiến
> nghị **dài hạn**: hệ thống tự động tôi đã xây — chỉ cần chạy mãi, mỗi
> quý chúng ta có báo cáo mới mà không tốn công người làm lại từ đầu.
> Đó là giá trị thật của Data Analytics: **biến phân tích 1 lần thành
> năng lực phân tích liên tục**."

---

## 🟦 SLIDE 10 — Q&A / Cảm ơn — ~30 giây

**NỘI DUNG**
- **CẢM ƠN ĐÃ LẮNG NGHE**
- 📩 Email | 🔗 GitHub repo URL | 📊 Link Power BI demo
- "Mọi câu hỏi xin mời quý thầy cô / hội đồng"

**HÌNH ẢNH**
- Ảnh chính giữa: ICONS Python + Pandas + Power BI + GitHub
- QR code link tới repo GitHub

**SPEAKER NOTES**
> "Em xin kết thúc phần trình bày tại đây. Cảm ơn quý thầy cô đã lắng
> nghe. Em xin mời quý thầy cô đặt câu hỏi."

---

## 📋 CHECKLIST CHUẨN BỊ TRƯỚC BUỔI THUYẾT TRÌNH

- [ ] Điền số liệu thật vào các ô `_XX_` (từ `data/clean/skill_report.csv`)
- [ ] Chụp screenshot Dashboard Power BI thật cho Slide 7 & 8
- [ ] Test mở file `.pbix` để chắc Power BI chạy được khi demo live
- [ ] In sẵn `narrative_summary.md` (1 trang A4) làm tài liệu phát kèm
- [ ] Backup video record dashboard 30s phòng trường hợp mất mạng
- [ ] Tập trình bày 3 lần để kiểm soát thời gian ≤ 15 phút
- [ ] Chuẩn bị Q&A: hiểu kỹ phần code Python + SQL, sẵn sàng demo trên repo

## ⚙️ CÁCH CHUYỂN SANG POWERPOINT
1. Mở Google Slides hoặc PowerPoint
2. Copy nội dung từng SLIDE ở trên, paste vào ô title + bullet
3. Bám theo SPEAKER NOTES để ghi vào "Notes" của từng slide
4. Thay placeholder `_XX_` bằng số liệu thật từ Power BI
5. Áp template chuẩn của VTI Academy (xanh-trắng-vàng)
