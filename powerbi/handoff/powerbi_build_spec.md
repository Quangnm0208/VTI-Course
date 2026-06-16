# Power BI — Đặc tả dựng báo cáo (Build Specification v2)

**Dự án:** Phân tích tín hiệu kỹ năng thị trường lập trình viên — VTI Academy
**Nguồn:** Stack Overflow Developer Survey (11.552 dev / 135 quốc gia / median $57.844) **+** ItViec (1.200 JD, scrape 2026-05-28)
**Đích:** 4 trang report, có bộ lọc đồng bộ. Đối chiếu giao diện với `reference/dashboard_reference.html`.

> File `.pbix` là nhị phân, phải dựng tay trong Power BI Desktop theo spec này. Mọi con số khớp với CSV trong `data/`.

---

## 1. Import dữ liệu (Get Data > Text/CSV)

Với từng file: **Delimiter = Comma**, **File Origin = 65001: Unicode (UTF-8)**, Transform Data để chỉnh kiểu, rồi Close & Apply.

| Bảng (Query) | File | Vai trò | Kiểu cột chính |
|---|---|---|---|
| dataset_overview | dataset_overview.csv | Fact KPI | value = Decimal |
| language_signal | language_signal.csv | Fact ngôn ngữ | worked/desired_next_year/net_change = Whole; growth_pct/desired_market_pct = Decimal |
| database_signal | database_signal.csv | Fact database | như trên |
| ide_overall | ide_overall.csv | Fact IDE | developer_count = Whole; usage_pct = Decimal |
| ide_by_role | ide_by_role.csv | Fact IDE×vai trò | developer_count = Whole |
| salary_by_language | salary_by_language.csv | Fact lương (toàn cầu) | median_salary/mean_salary = Whole |
| role_priority | role_priority.csv | Fact + Dim vai trò | hiring_priority_score = Decimal |
| country_distribution | country_distribution.csv | Fact quốc gia | count = Whole; pct = Decimal |
| jd_keyword_map | jd_keyword_map.csv | Ref từ khoá JD | text |
| training_roadmap | training_roadmap.csv | Ref lộ trình | text |
| interview_rubric | interview_rubric.csv | Ref rubric | weight_pct = Whole |
| strategic_recommendations | strategic_recommendations.csv | Ref khuyến nghị | text |
| **vn_itviec_skill_demand** | vn_itviec_skill_demand.csv | **MỚI** Fact cầu VN | jobs_count = Whole; pct_of_jobs = Decimal |
| **vn_salary_benchmark** | vn_salary_benchmark.csv | **MỚI** Fact lương VN | annual_usd_min/max = Whole |
| **vn_vs_global_compare** | vn_vs_global_compare.csv | **MỚI** Ref đối chiếu | vn_pct_of_jd/global_worked = Decimal/Whole |

`itviec_jobs_raw.csv` (1.200 dòng thô) chỉ để kiểm chứng / tổng hợp lại — KHÔNG cần đưa vào model.

---

## 2. Mô hình (Star schema)

- **DimSignal** (Enter Data): cột `signal` = { Emerging, Stable, Declining }. Quan hệ 1‑* tới `language_signal[signal]` và `database_signal[signal]`.
- **DimRole** (= `role_priority[role]`): quan hệ 1‑* tới `ide_by_role[role]`.
- Các bảng còn lại (gồm 3 bảng VN) để **disconnected** — chỉ phục vụ KPI/visual riêng, không join.

---

## 3. Số đo DAX (bảng `_Measures`)

```DAX
Total Respondents = CALCULATE(MAX(dataset_overview[value]), dataset_overview[metric]="Total respondents")   -- 11.552
Total Countries   = CALCULATE(MAX(dataset_overview[value]), dataset_overview[metric]="Countries covered")   -- 135
Median Salary     = CALCULATE(MAX(dataset_overview[value]), dataset_overview[metric]="Median salary USD")   -- 57.844

Top Current Language =
VAR t = TOPN(1, ALL(language_signal), language_signal[worked], DESC)
RETURN CONCATENATEX(t, language_signal[language], ", ")   -- JavaScript

Top Database =
VAR t = TOPN(1, ALL(database_signal), database_signal[desired_next_year], DESC)
RETURN CONCATENATEX(t, database_signal[database], ", ")   -- PostgreSQL

Emerging Skill Count =
CALCULATE(COUNTROWS(language_signal), language_signal[signal]="Emerging")
+ CALCULATE(COUNTROWS(database_signal), database_signal[signal]="Emerging")   -- 11

Growth Gap = SUM(language_signal[net_change])

-- MỚI cho trang Việt Nam
VN Total JD = 1200
VN Top Skill =
VAR t = TOPN(1, ALL(vn_itviec_skill_demand), vn_itviec_skill_demand[jobs_count], DESC)
RETURN CONCATENATEX(t, vn_itviec_skill_demand[skill], ", ")   -- English (kỹ năng), Python/AI (kỹ thuật)
VN Senior vs Global % =
DIVIDE(30000, [Median Salary])   -- ~0,52  (lương senior VN ~ 52% mốc toàn cầu)
```

---

## 4. Bố cục 4 trang + bộ lọc

### Bộ lọc dùng chung (Slicer — Sync Slicers giữa các trang)
1. **Tín hiệu (Signal)** — `DimSignal[signal]` dạng button: Tất cả / Emerging / Stable / Declining. Lọc các fact ngôn ngữ & database.
2. **Top N** — dùng **Top N filter** trên từng visual xếp hạng (Filters pane → Top N theo measure tương ứng): 5 / 10 / All. (Hoặc tham số `What-if` để chuyển nhanh.)
3. *(tuỳ chọn)* **Tô tín hiệu** — trong Power BI thể hiện bằng **Conditional formatting / Data colors theo `signal`** trên các bar ngôn ngữ (Emerging=#10b981, Stable=#6e76dd, Declining=#dc2626). Bản HTML mẫu có nút bật/tắt; Power BI có thể để mặc định bật.

### Trang 1 — Executive Overview
KPI cards: Total Respondents, Total Countries, Median Salary, Median exp (5), Full‑time (96,2%), Avg langs (5,2).
Visuals: Top ngôn ngữ `worked` (bar h), Top ngôn ngữ `desired_next_year` (bar h), Phân bố quốc gia `country_distribution[pct]` (bar h).

### Trang 2 — Skill Demand Deep Dive
Database `worked` vs `desired_next_year` (clustered bar) · Skill‑gap `net_change` (diverging bar, màu theo dấu) · Lương theo ngôn ngữ `salary_by_language[median_salary]` (bar h) · IDE phổ biến `ide_overall[usage_pct]` (bar h) · IDE theo vai trò `ide_by_role` (Matrix: Rows=role, Values=developer_count).

### Trang 3 — Việt Nam (ItViec)  ← MỚI
| Visual | Loại | Nguồn |
|---|---|---|
| KPI: 1.200 JD · 28/05/2026 · Top skill · 0% lương công khai | Card | vn_itviec_skill_demand / cố định |
| Cầu kỹ năng VN | Bar h | vn_itviec_skill_demand[pct_of_jobs] |
| Đối chiếu VN vs Toàn cầu | Table | vn_vs_global_compare |
| **So sánh lương VN vs toàn cầu** | **Bar phân khoảng** (min→max) + đường tham chiếu | vn_salary_benchmark (annual_usd_min/max); reference line tại $57.844 |

Lưu ý hiển thị trên trang VN: ghi rõ "ItViec ẩn lương (0/1.200 JD) → lương VN từ TopDev/Reco/Glassdoor 2024–2026; mốc toàn cầu từ Stack Overflow."

### Trang 4 — Strategic Recommendation
Ưu tiên tuyển dụng `role_priority[hiring_priority_score]` (Matrix/bar) · Kỹ năng Emerging `growth_pct` (bar, lọc signal=Emerging) · Lộ trình `training_roadmap` (4 card/table) · 3 khuyến nghị `strategic_recommendations` (card) · Rubric `interview_rubric[weight_pct]` (bar).

---

## 5. Các bước dựng .pbix
1. Get Data > Text/CSV → import 15 CSV (UTF‑8) → Close & Apply.
2. Model view → tạo DimSignal, DimRole (Enter Data) + kéo quan hệ mục 2.
3. Tạo `_Measures`, dán DAX mục 3.
4. Dựng 4 trang (đặt tên: Executive Overview · Skill Demand · Viet Nam · Strategic Recommendation) theo mục 4; bật **Sync Slicers** cho Signal.
5. Áp Data colors theo `signal` (mục 4 — Tô tín hiệu) và Top N filter cho các bar xếp hạng.
6. Đối chiếu với `reference/dashboard_reference.html` (11.552 · 135 · JavaScript · PostgreSQL · DevOps $71.036 · VN Python/AI 19,3% · VN senior ~52% mốc toàn cầu).
7. File > Save As → `skill_market_dashboard.pbix`.

---

## 6. Từ điển dữ liệu — 3 file VN mới

**vn_itviec_skill_demand.csv** — `skill`, `jobs_count` (số JD có kỹ năng), `pct_of_jobs` (% trên 1.200 JD).
**vn_salary_benchmark.csv** — `tier`, `annual_usd_min`, `annual_usd_max`, `kind` (vietnam / *_reference), `source`.
**vn_vs_global_compare.csv** — `rank`, `vn_skill`, `vn_pct_of_jd`, `global_language`, `global_worked`.
