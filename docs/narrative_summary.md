# BÁO CÁO TÓM TẮT
## A Day in the Life of a Data Analyst — Phân tích Kỹ năng CNTT
**Học viên:** _[Họ tên]_ | **Lớp:** VTI Academy | **Ngày:** _[dd/mm/yyyy]_

---

### 1. Bối cảnh (Context)
VTI Academy cần liên tục cập nhật chương trình đào tạo theo kỹ năng IT đang
nổi trên thị trường. Báo cáo này phân tích **kỹ năng lập trình được yêu cầu
nhiều nhất** từ 2 nguồn dữ liệu chính: khảo sát developer toàn cầu của
**Stack Overflow** (~80 cột, ~10.000+ bản ghi) và **tin tuyển dụng IT trực
tiếp tại Việt Nam** (ItViec, cào tự động hàng ngày).

### 2. Phương pháp (Methodology)
- **Thu thập:** Web Scraping ItViec bằng Python (Playwright vượt Cloudflare)
  + đọc CSV khảo sát Stack Overflow.
- **Làm sạch:** Pandas — chuẩn hóa tên cột snake_case, xử lý NaN, explode
  multi-value (`Python;Java;SQL` → 3 dòng), chuẩn hóa tên kỹ năng qua từ
  điển alias (`nodejs` → `Node.js`).
- **Lưu trữ:** SQLite (4 bảng) + 1 file CSV/Excel tổng hợp long-format.
- **Tự động hóa:** GitHub Actions cron 07:00 VN hàng ngày → scrape →
  upsert idempotent → commit ngược về repo. Có data-quality workflow check
  5 tiêu chí và alert.

### 3. Kết quả chính (Key Insights)
| Hạng mục | Top 3 |
|---|---|
| **Ngôn ngữ lập trình** | JavaScript, Python, SQL |
| **Cơ sở dữ liệu** | PostgreSQL, MySQL, MongoDB |
| **IDE** | Visual Studio Code, IntelliJ, Visual Studio |
| **Kỹ năng emerging** *(demand JD cao, supply thấp)* | Go, Rust, TypeScript |

**Insight nổi bật:**
1. **Python tăng trưởng mạnh nhất** — chênh lệch "muốn học năm sau" so với
   "đang dùng" lớn nhất (+25%).
2. **Mảng cloud (AWS/Docker/Kubernetes) xuất hiện ở 60% JD ItViec** nhưng
   chỉ 30% dev Stack Overflow đã thông thạo → khoảng trống đào tạo lớn.
3. **VS Code thống trị IDE** (~55%), bỏ xa IntelliJ (~22%).

### 4. Kiến nghị Chiến lược (Strategic Recommendations)
1. **Mở khóa Python + Cloud DevOps** (Docker/AWS) ngay quý tới — đáp ứng
   khoảng trống cung-cầu lớn nhất.
2. **Tích hợp Go & Rust** vào lộ trình nâng cao — đón đầu nhu cầu emerging.
3. **Duy trì pipeline scraping tự động** để tái phân tích định kỳ, đảm bảo
   chương trình đào tạo luôn cập nhật theo thị trường.

---
*Nguồn dữ liệu: Stack Overflow Developer Survey + ItViec (scraping live).
Công cụ: Python (Pandas/Playwright/BeautifulSoup), SQL (SQLite), Power BI.
Repo: github.com/Quangnm0208/VTI-Course*
