# Dựng `.pbix` từ CSV — từng bước (sau khi đã Load hết data)

> Đã import 10 bảng từ `powerbi/*.csv`. Dưới đây là **DAX + cách kéo field + sort + màu**
> để dựng nhanh. Power BI: trục của *Clustered bar* = **Y-axis (danh mục)** + **X-axis (giá trị)**;
> của *Clustered column* = **X-axis (danh mục)** + **Y-axis (giá trị, nhiều cột được)**.

## BƯỚC 0 — Theme 3 màu (làm 1 lần)
**View → Themes → Browse for themes** → chọn file `powerbi/theme_vti_3color.json`
(màu: chàm `#3b3fbf` · xanh lá `#10b981` · xám `#94a3b8`).

## BƯỚC 1 — Tạo Measures (Modeling → New measure, dán từng dòng)
```DAX
Total Respondents = MAXX(FILTER(dataset_overview, dataset_overview[metric]="Total respondents"), dataset_overview[value])
Total Countries   = MAXX(FILTER(dataset_overview, dataset_overview[metric]="Countries covered"), dataset_overview[value])
Median Salary USD = MAXX(FILTER(dataset_overview, dataset_overview[metric]="Median salary USD"), dataset_overview[value])
Median Exp Years  = MAXX(FILTER(dataset_overview, dataset_overview[metric]="Median professional coding years"), dataset_overview[value])
Full-time Pct     = MAXX(FILTER(dataset_overview, dataset_overview[metric]="Employed full-time percentage"), dataset_overview[value])
Emerging Language Count = CALCULATE(COUNTROWS(language_signal), language_signal[signal]="Emerging")
Top Desired Language = MAXX(TOPN(1, language_signal, language_signal[desired_next_year], DESC), language_signal[language])
Top Database         = MAXX(TOPN(1, database_signal, database_signal[desired_next_year], DESC), database_signal[database])
VN Total JD   = 1200
VN Top Skill  = MAXX(TOPN(1, vn_itviec_skill_demand, vn_itviec_skill_demand[jobs_count], DESC), vn_itviec_skill_demand[skill])
```
**Format measure** (tab Measure tools): `Total Respondents`/`VN Total JD` → Whole number, ✔ thousands.
`Median Salary USD` → Currency `$ English (US)`, 0 decimals. `Full-time Pct`,`Median Exp Years` → Decimal 1.

---

## TRANG 1 — Tổng quan
| Visual | Loại | Field (kéo vào) | Sort |
|---|---|---|---|
| KPI ×5 | **Card** | lần lượt: `Total Respondents` · `Total Countries` · `Median Salary USD` · `Emerging Language Count` · `Top Desired Language` | — |
| Ngôn ngữ đang dùng | **Clustered bar** | Y-axis `language_signal[language]` · X-axis `worked` | `...` → Sort axis → **worked, Descending** |
| Ngôn ngữ muốn dùng | **Clustered bar** | Y-axis `language_signal[language]` · X-axis `desired_next_year` | Sort → desired_next_year, Desc |
| Top quốc gia | **Clustered column** | X-axis `country_distribution[country]` · Y-axis `pct` | Sort → pct, Desc |
| **Slicer 1** | **Slicer** | Field `language_signal[signal]` | — |
| **Slicer 2** | **Slicer** | Field `role_priority[priority_band]` | — |

## TRANG 2 — Cung–cầu kỹ năng
| Visual | Loại | Field | Sort |
|---|---|---|---|
| Database: đang vs muốn | **Clustered column** | X-axis `database_signal[database]` · Y-axis **`worked` + `desired_next_year`** | Sort → desired_next_year, Desc |
| Skill-gap ngôn ngữ | **Clustered bar** | Y-axis `language_signal[language]` · X-axis `net_change` | Sort → net_change, Desc |
| Lương theo ngôn ngữ | **Clustered bar** | Y-axis `salary_by_language[language]` · X-axis `median_salary` | Sort → median_salary, Desc |
| IDE phổ biến | **Clustered bar** | Y-axis `ide_overall[ide]` · X-axis `usage_pct` | Sort → usage_pct, Desc |

## TRANG 3 — Việt Nam (ItViec)
| Visual | Loại | Field | Ghi chú |
|---|---|---|---|
| Card ×2 | **Card** | `VN Total JD` · `VN Top Skill` | — |
| Cầu kỹ năng VN | **Clustered bar** | Y-axis `vn_itviec_skill_demand[skill]` · X-axis `pct_of_jobs` | Filter visual: **Top N = 12 by pct_of_jobs**; Sort Desc |
| Lương VN theo cấp | **Clustered column** | X-axis `vn_salary_benchmark[tier]` · Y-axis `annual_usd_min` + `annual_usd_max` | — |
| VN vs toàn cầu | **Table** | Columns: `rank`,`vn_skill`,`vn_pct_of_jd`,`global_language`,`global_worked` (bảng `vn_vs_global_compare`) | — |

## TRANG 4 — Khuyến nghị (tuỳ chọn)
| Visual | Loại | Field | Sort |
|---|---|---|---|
| Ưu tiên tuyển dụng | **Clustered bar** | Y-axis `role_priority[role]` · X-axis `hiring_priority_score` | Sort Desc |
| Emerging ngôn ngữ | **Clustered bar** | Y-axis `language_signal[language]` · X-axis `growth_pct` | Filter Top 8 by growth_pct; Sort Desc |

---

## BƯỚC CUỐI
**File → Save As → `skill_market_dashboard.pbix`**. Xong — đủ ≥5 visual + 2 slicer, trả lời 4 câu hỏi (ngôn ngữ · database · IDE · emerging).

### Mẹo nhanh
- **Sort:** bấm `...` (More options) góc visual → **Sort axis** → chọn cột giá trị → **Sort descending**.
- **Đổi tên trục/tiêu đề:** Format (cây cọ) → General → Title.
- **Top N:** kéo cột vào ô **Filters on this visual** → Filter type = Top N → nhập N, “By value” = chính cột đó.
