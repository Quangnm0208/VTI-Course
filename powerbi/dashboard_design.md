# Power BI Dashboard - Đặc tả thiết kế (Build Specification)

**Dự án:** Phân tích tín hiệu kỹ năng thị trường Lập trình viên (Stack Overflow Developer Survey)
**Quy mô dữ liệu:** 11.552 lập trình viên / 135 quốc gia / median salary $57.844
**Mục tiêu báo cáo:** Biến dữ liệu khảo sát thành khuyến nghị tuyển dụng và lộ trình đào tạo cho VTI Academy.

> File này là bản thiết kế để dựng báo cáo `.pbix` trong Power BI Desktop.
> Bản demo chạy được ngay (nguồn ảnh chụp màn hình minh hoạ) nằm ở `powerbi/dashboard.html` (Plotly) — mở bằng trình duyệt để xem trước bố cục và các con số trước khi dựng lại trong Power BI.

---

## 1. Import dữ liệu và mô hình (Data Model)

### 1.1 Import các CSV nguồn
Tất cả nguồn dữ liệu đã được làm sạch và tổng hợp sẵn trong thư mục `powerbi/`. Trong Power BI Desktop:

1. **Get Data > Text/CSV** cho từng file dưới đây.
2. Ở cửa sổ preview, đặt **Delimiter = Comma** và **File Origin = 65001: Unicode (UTF-8)** (các file có BOM và chứa tiếng Việt — chọn UTF-8 để không lỗi dấu).
3. Bấm **Transform Data** để mở Power Query, kiểm tra kiểu dữ liệu (các cột `worked`, `desired_next_year`, `net_change`, `developer_count`, `count` là *Whole Number*; `growth_pct`, `usage_pct`, `pct`, `median_salary`, `mean_salary`, `mean_vs_global_pct`, `hiring_priority_score` là *Decimal Number*), rồi **Close & Apply**.

| Bảng (Query) | File nguồn | Vai trò trong model |
|---|---|---|
| `dataset_overview` | `powerbi/dataset_overview.csv` | Fact tổng quan (metric / value) |
| `language_signal` | `powerbi/language_signal.csv` | Fact - tín hiệu ngôn ngữ |
| `database_signal` | `powerbi/database_signal.csv` | Fact - tín hiệu database |
| `ide_overall` | `powerbi/ide_overall.csv` | Fact - IDE tổng thể |
| `ide_by_role` | `powerbi/ide_by_role.csv` | Fact - IDE theo vai trò |
| `salary_by_language` | `powerbi/salary_by_language.csv` | Fact - lương theo ngôn ngữ |
| `role_priority` | `powerbi/role_priority.csv` | Fact + lookup - vai trò & ưu tiên tuyển |
| `country_distribution` | `powerbi/country_distribution.csv` | Fact - phân bố quốc gia |
| `jd_keyword_map` | `powerbi/jd_keyword_map.csv` | Bảng tham chiếu - từ khoá JD |
| `training_roadmap` | `powerbi/training_roadmap.csv` | Bảng tham chiếu - lộ trình đào tạo |
| `interview_rubric` | `powerbi/interview_rubric.csv` | Bảng tham chiếu - rubric phỏng vấn |
| `strategic_recommendations` | `powerbi/strategic_recommendations.csv` | Bảng tham chiếu - khuyến nghị chiến lược |

### 1.2 Mô hình ngôi sao (Star schema)
Mỗi danh mục kỹ năng (`language_signal`, `database_signal`) là một **fact tín hiệu kỹ năng** với cùng cấu trúc (`worked`, `desired_next_year`, `net_change`, `growth_pct`, `desired_market_pct`, `signal`). Ta thêm 2 dimension nhỏ để lọc xuyên suốt:

- **DimSignal** (lookup): tạo bảng tĩnh bằng **Enter Data** với một cột `signal` = { `Emerging`, `Stable`, `Declining` }.
  Quan hệ 1-* tới `language_signal[signal]` và `database_signal[signal]`.
- **DimRole** (lookup): dùng `role_priority[role]` làm dimension vai trò.
  Quan hệ 1-* tới `ide_by_role[role]`.

Sơ đồ quan hệ:

```
                 DimSignal (signal)
                 /                \
                / 1            1  \
               *                  *
      language_signal      database_signal
                                          
                 DimRole (role)
                 /            \
                / 1        1  \
               *              *
        ide_by_role     role_priority
```

`salary_by_language`, `ide_overall`, `country_distribution`, `dataset_overview` đứng độc lập (disconnected) — chỉ dùng để hiển thị KPI và biểu đồ riêng, không cần join.
`jd_keyword_map`, `training_roadmap`, `interview_rubric`, `strategic_recommendations` là bảng tham chiếu hiển thị dạng table.

> Lưu ý: vì dữ liệu đã được tiền-tổng hợp (mỗi dòng là một kỹ năng), số đo chủ yếu dùng `SUM`/`MAX`/`SELECTEDVALUE` chứ không đếm từng dòng khảo sát.

---

## 2. Các số đo DAX (Measures)

Tạo một bảng đo `_Measures` (Enter Data, 1 cột rỗng) để gom tất cả measure. Tối thiểu 6 measure bắt buộc dưới đây (đã đủ và dư yêu cầu):

```DAX
-- 1) Tổng số lập trình viên tham gia khảo sát
Total Respondents =
CALCULATE(
    MAX(dataset_overview[value]),
    dataset_overview[metric] = "Total respondents"
)   -- = 11.552

-- 2) Tổng số quốc gia
Total Countries =
CALCULATE(
    MAX(dataset_overview[value]),
    dataset_overview[metric] = "Countries covered"
)   -- = 135

-- 3) Median Salary (USD) tham chiếu toàn cục
Median Salary =
CALCULATE(
    MAX(dataset_overview[value]),
    dataset_overview[metric] = "Median salary USD"
)   -- = 57.844

-- 4) Ngôn ngữ được mong muốn nhất (Top Desired Language) qua TOPN
Top Desired Language =
VAR t = TOPN(1, ALL(language_signal), language_signal[desired_next_year], DESC)
RETURN CONCATENATEX(t, language_signal[language], ", ")   -- = JavaScript

-- 5) Ngôn ngữ đang dùng nhiều nhất (Top Current Language)
Top Current Language =
VAR t = TOPN(1, ALL(language_signal), language_signal[worked], DESC)
RETURN CONCATENATEX(t, language_signal[language], ", ")   -- = JavaScript

-- 6) Database dẫn đầu nhu cầu (Top Database)
Top Database =
VAR t = TOPN(1, ALL(database_signal), database_signal[desired_next_year], DESC)
RETURN CONCATENATEX(t, database_signal[database], ", ")   -- = PostgreSQL

-- 7) Đếm số kỹ năng "Emerging" (ngôn ngữ + database)
Emerging Skill Count =
CALCULATE(COUNTROWS(language_signal), language_signal[signal] = "Emerging")
  + CALCULATE(COUNTROWS(database_signal), database_signal[signal] = "Emerging")

-- 8) Growth Gap (khoảng cách cung-cầu kỹ năng) - dùng cho diverging bar
Growth Gap = SUM(language_signal[net_change])

-- 9) % Share thị phần mong muốn của kỹ năng đang được chọn
Desired % Share = SELECTEDVALUE(language_signal[desired_market_pct]) / 100

-- 10) Median salary của ngôn ngữ đang chọn (cho lollipop/bar lương)
Lang Median Salary = SUM(salary_by_language[median_salary])
```

---

## 3. Bố cục báo cáo - 3 trang

### Page 1 — Executive Overview
*Mục tiêu: lãnh đạo nắm toàn cảnh trong 10 giây.*

**KPI Cards (5 thẻ Card):**
| # | Card | Trường / Measure | Nguồn |
|---|---|---|---|
| 1 | Total respondents = **11.552** | `[Total Respondents]` | dataset_overview |
| 2 | Total countries = **135** | `[Total Countries]` | dataset_overview |
| 3 | Top current language = **JavaScript** | `[Top Current Language]` | language_signal |
| 4 | Top desired language = **JavaScript** | `[Top Desired Language]` | language_signal |
| 5 | Top database = **PostgreSQL** | `[Top Database]` | database_signal |

**Biểu đồ:**
| Visual | Loại | Axis / Field | Nguồn (CSV.cột) |
|---|---|---|---|
| Top 10 ngôn ngữ đang dùng | Bar chart (Clustered bar, ngang) | Y-axis (Category) = `language`; X-axis (Value) = `worked`; sắp giảm dần, Top N filter = 10 | language_signal.worked |
| Top 10 ngôn ngữ mong muốn | Bar chart (Clustered bar, ngang) | Y-axis = `language`; X-axis = `desired_next_year`; Top N = 10 | language_signal.desired_next_year |

**Slicers (3):**
1. **Country** — `country_distribution[country]` (dropdown).
2. **Employment** — dùng `dataset_overview` (metric "Employed full-time percentage") hoặc tạo slicer minh hoạ; để chuẩn star, gắn nhãn "Employment" lọc theo cột phân loại nếu có. (List).
3. **YearsCodePro group** — slicer nhóm số năm kinh nghiệm (median = 5 năm) (List).

### Page 2 — Skill Demand Deep Dive
*Mục tiêu: đào sâu cung-cầu từng nhóm kỹ năng.*

| Visual | Loại | Axis / Field | Nguồn (CSV.cột) | DAX |
|---|---|---|---|---|
| Database: đang dùng vs mong muốn | Clustered bar chart | Axis = `database`; Values = `worked`, `desired_next_year` | database_signal | — |
| IDE theo vai trò | Matrix (hoặc Heatmap qua conditional formatting trên `developer_count`) | Rows = `role`; Columns = `ide`; Values = `developer_count` | ide_by_role | — |
| Skill-gap (chênh lệch cung-cầu) | Diverging bar chart (bar có giá trị âm/dương) | Axis = `language`; Value = `net_change`; màu theo dấu | language_signal.net_change | `[Growth Gap]` |
| Lương theo ngôn ngữ | Lollipop / Bar chart | Axis = `language`; Value = `median_salary`; sắp giảm dần | salary_by_language.median_salary | `[Lang Median Salary]` |

**Slicers (2):**
1. **Skill category (Signal)** — `DimSignal[signal]` { Emerging / Stable / Declining } (button slicer) — lọc đồng thời language_signal & database_signal.
2. **Developer type (role)** — `DimRole[role]` (dropdown) — lọc ma trận IDE theo vai trò.

### Page 3 — Strategic Recommendation
*Mục tiêu: chốt khuyến nghị đào tạo & tuyển dụng.*

| Visual | Loại | Axis / Field | Nguồn (CSV.cột) | DAX |
|---|---|---|---|---|
| Nhóm kỹ năng × Ưu tiên | Matrix | Rows = `role`; Values = `hiring_priority_score`, `priority_band`, `median_salary`; sắp theo score | role_priority | — |
| Kỹ năng nổi lên (Emerging) | Bar chart (sắp theo growth_pct giảm dần) | Axis = `language`; Value = `growth_pct`; lọc `signal = "Emerging"` | language_signal.growth_pct | `[Emerging Skill Count]` (KPI phụ) |
| Khoá học đề xuất | Table | Cột: `phase`, `training_block`, `target_roles`, `hr_reason` (+ `horizon`, `recommendation`, `evidence` từ strategic_recommendations) | training_roadmap + strategic_recommendations | — |
| 3 thẻ ưu tiên chương trình | 3 Card | Card 1: "Nền chung: VS Code + Git + PostgreSQL"; Card 2: "Track ưu tiên: Cloud & DevOps ($71.036)"; Card 3: "Đón đầu: TypeScript / Go / Kotlin / Rust" | training_roadmap / strategic_recommendations / role_priority | — |

**Slicer:** kế thừa **Skill category (Signal)** từ Page 2 (Sync Slicers) để lọc biểu đồ Emerging.

---

## 4. Kiểm tra điều kiện tối thiểu (Minimum requirements)

- **Số visual/card:** Trang 1 có 7 (5 card + 2 bar), Trang 2 có 4, Trang 3 có 6 (matrix + bar + table + 3 card) → **tổng 17 visual/card**, vượt xa yêu cầu ≥ 5. ✔
- **Số slicer:** Trang 1 có 3, Trang 2 có 2, Trang 3 có 1 (sync) → ≥ 2. ✔
- **Số đo DAX:** 10 measure (≥ 6). ✔
- **Tương tác:** slicer Signal & Role lan toả qua các fact nhờ DimSignal/DimRole. ✔

---

## 5. Cách tạo file .pbix (How to produce the .pbix)

1. Mở **Power BI Desktop** (Windows). File mới rỗng.
2. **Get Data > Text/CSV** → import lần lượt 12 CSV trong `powerbi/` (mục 1.1), đặt UTF-8, Close & Apply.
3. Vào **Model view**: tạo `DimSignal`, `DimRole` (Enter Data) và kéo quan hệ như mục 1.2.
4. Tạo bảng `_Measures`, dán toàn bộ DAX ở mục 2.
5. Dựng 3 trang report theo mục 3 (đặt tên trang: *Executive Overview*, *Skill Demand Deep Dive*, *Strategic Recommendation*).
6. Bật **Sync Slicers** cho slicer Signal giữa Page 2 và Page 3.
7. Đối chiếu các con số với `powerbi/dashboard.html` để đảm bảo khớp (11.552 / 135 / JavaScript / PostgreSQL / DevOps $71.036).
8. **File > Save As** → lưu `powerbi/skill_market_dashboard.pbix`. Đây là file nhị phân `.pbix` cần nộp.
9. (Tuỳ chọn) **File > Export > PDF** để có bản báo cáo tĩnh kèm theo.
