"""
generate_deliverables.py — Sinh toàn bộ sản phẩm nộp từ một bộ số liệu duy nhất.

Chạy:
    python analysis/generate_deliverables.py

Đầu ra:
    data/clean/*.csv                 — các bảng tổng hợp (nguồn cho Power BI)
    data/clean/skill_market_insight.xlsx — 1 workbook nhiều sheet
    powerbi/dashboard.html           — dashboard tương tác (Plotly, mở bằng browser)

PowerPoint được sinh riêng ở analysis/build_pptx.py để tách phần phụ thuộc.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent))
import market_insight_data as D  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
PBI = ROOT / "powerbi"
CLEAN.mkdir(parents=True, exist_ok=True)
PBI.mkdir(parents=True, exist_ok=True)

COL = {
    "primary": "#2563eb", "good": "#16a34a", "bad": "#dc2626",
    "accent": "#9333ea", "amber": "#f59e0b", "ink": "#0f172a",
    "muted": "#64748b",
}


# -----------------------------------------------------------------------------
# 1. Xuất CSV + Excel (nguồn dữ liệu cho Power BI / SQL)
# -----------------------------------------------------------------------------
def export_tables() -> dict[str, pd.DataFrame]:
    tables = {name: fn() for name, fn in D.ALL_TABLES.items()}
    for name, df in tables.items():
        df.to_csv(CLEAN / f"{name}.csv", index=False, encoding="utf-8-sig")
        df.to_csv(PBI / f"{name}.csv", index=False, encoding="utf-8-sig")

    xlsx = CLEAN / "skill_market_insight.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        for name, df in tables.items():
            df.to_excel(w, sheet_name=name[:31], index=False)
    print(f"[ok] {len(tables)} bảng -> data/clean/ + powerbi/ + {xlsx.name}")
    return tables


# -----------------------------------------------------------------------------
# 2. Dashboard tương tác (Plotly) — 6 chart + tiêu đề + KPI
# -----------------------------------------------------------------------------
def build_dashboard(tables: dict[str, pd.DataFrame]) -> None:
    lang = tables["language_signal"]
    db = tables["database_signal"]
    sal = tables["salary_by_language"]
    role = tables["role_priority"]
    ide = tables["ide_overall"]
    ov = tables["dataset_overview"].set_index("metric")["value"]

    figs = []

    # (a) Top ngôn ngữ muốn dùng năm sau — bar ngang
    d = lang.sort_values("desired_next_year").tail(12)
    f = go.Figure(go.Bar(
        x=d["desired_next_year"], y=d["language"], orientation="h",
        marker_color=COL["primary"],
        text=d["desired_next_year"], textposition="outside"))
    f.update_layout(title="① Top ngôn ngữ MUỐN dùng năm tới (số dev)")
    figs.append(f)

    # (b) Net-change ngôn ngữ — diverging
    d = lang.reindex(lang["net_change"].abs().sort_values().index).tail(12)
    f = go.Figure(go.Bar(
        x=d["net_change"], y=d["language"], orientation="h",
        marker_color=[COL["good"] if v >= 0 else COL["bad"] for v in d["net_change"]],
        text=d["growth_pct"].map(lambda v: f"{v:+.0f}%"), textposition="outside"))
    f.update_layout(title="② Thay đổi ròng nhu cầu ngôn ngữ (muốn − đang dùng)")
    figs.append(f)

    # (c) Database đang dùng vs muốn dùng — grouped
    d = db.head(10)
    f = go.Figure()
    f.add_bar(x=d["database"], y=d["worked"], name="Đang dùng", marker_color=COL["muted"])
    f.add_bar(x=d["database"], y=d["desired_next_year"], name="Muốn dùng", marker_color=COL["accent"])
    f.update_layout(title="③ Cơ sở dữ liệu: đang dùng vs muốn dùng", barmode="group")
    figs.append(f)

    # (d) IDE phổ biến — bar
    d = ide.sort_values("developer_count")
    f = go.Figure(go.Bar(
        x=d["developer_count"], y=d["ide"], orientation="h", marker_color=COL["amber"],
        text=d["usage_pct"].map(lambda v: f"{v:.0f}%"), textposition="outside"))
    f.update_layout(title="④ IDE phổ biến nhất (top 10)")
    figs.append(f)

    # (e) Lương theo ngôn ngữ — lollipop (median)
    d = sal.sort_values("median_salary").tail(12)
    f = go.Figure()
    for _, r in d.iterrows():
        f.add_shape(type="line", x0=0, x1=r["median_salary"], y0=r["language"],
                    y1=r["language"], line=dict(color=COL["muted"], width=2))
    f.add_trace(go.Scatter(
        x=d["median_salary"], y=d["language"], mode="markers+text",
        marker=dict(size=11, color=COL["good"]),
        text=d["median_salary"].map(lambda v: f"${v/1000:.0f}k"),
        textposition="middle right"))
    f.update_layout(title="⑤ Lương trung vị theo ngôn ngữ (USD)")
    figs.append(f)

    # (f) Bubble: lương vs tăng trưởng (kích thước = nhu cầu)
    cross = lang.merge(sal[["language", "median_salary"]], on="language", how="inner")
    f = go.Figure(go.Scatter(
        x=cross["growth_pct"], y=cross["median_salary"], mode="markers+text",
        marker=dict(size=cross["desired_next_year"] / 120, color=cross["growth_pct"],
                    colorscale="RdYlGn", showscale=True, line=dict(width=1, color="white")),
        text=cross["language"], textposition="top center"))
    f.add_vline(x=0, line_dash="dot", line_color=COL["muted"])
    f.update_layout(title="⑥ Lương vs tăng trưởng (size = nhu cầu năm tới)",
                    xaxis_title="growth % (muốn/đang)", yaxis_title="median salary USD")
    figs.append(f)

    # Layout chung
    for f in figs:
        f.update_layout(
            template="plotly_white", height=430,
            margin=dict(l=10, r=20, t=50, b=30),
            title_font=dict(size=15, color=COL["ink"]),
            font=dict(family="Segoe UI, Arial", size=12),
        )

    # KPI cards
    kpis = [
        ("Developers khảo sát", f"{int(ov['Total respondents']):,}"),
        ("Quốc gia", f"{int(ov['Countries covered'])}"),
        ("Median salary", f"${int(ov['Median salary USD']):,}"),
        ("Ngôn ngữ Emerging", "Rust · Go · Zig · Elixir"),
        ("Database trục chính", "PostgreSQL (dẫn đầu)"),
        ("IDE chuẩn onboarding", "VS Code (kỳ SO gần nhất)"),
    ]
    cards = "".join(
        f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in kpis
    )

    # Slicer (lọc theo nhóm tín hiệu) — JS thuần lọc chart ① và ②
    def div(fig, _id):
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id=_id)

    ids = [f"chart{i}" for i in range(len(figs))]
    blocks = "".join(
        f'<div class="chart">{div(f, i)}</div>' for f, i in zip(figs, ids))

    html = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VTI Academy — Dashboard Phân tích Kỹ năng CNTT</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
 body{{font-family:'Segoe UI',Arial,sans-serif;margin:0;background:#f1f5f9;color:#0f172a}}
 header{{background:linear-gradient(120deg,#1e3a8a,#2563eb);color:#fff;padding:22px 32px}}
 header h1{{margin:0;font-size:24px}} header p{{margin:6px 0 0;opacity:.9}}
 .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;padding:20px 32px}}
 .card{{background:#fff;border-radius:12px;padding:14px 16px;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
 .card .k{{font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:.04em}}
 .card .v{{font-size:20px;font-weight:700;margin-top:4px;color:#1e3a8a}}
 .filters{{padding:0 32px 4px}} .filters label{{font-size:13px;color:#334155;margin-right:8px}}
 select{{padding:6px 10px;border-radius:8px;border:1px solid #cbd5e1;background:#fff}}
 .grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;padding:14px 32px 40px}}
 .chart{{background:#fff;border-radius:12px;padding:8px;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
 footer{{padding:18px 32px;color:#64748b;font-size:12px}}
 @media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header>
 <h1>VTI Academy — Phân tích Kỹ năng Công nghệ Thông tin</h1>
 <p>Nguồn: Stack Overflow Developer Survey ({int(ov['Total respondents']):,} dev · {int(ov['Countries covered'])} quốc gia)
    + tin tuyển dụng ItViec · Trả lời 4 câu hỏi: Ngôn ngữ · Database · IDE · Kỹ năng nổi (emerging)</p>
</header>
<div class="kpis">{cards}</div>
<div class="filters">
 <label for="sig">Bộ lọc tín hiệu (chart ① ②):</label>
 <select id="sig" onchange="applyFilter()">
   <option value="all">Tất cả</option>
   <option value="Emerging">Emerging (đang nổi)</option>
   <option value="Stable">Stable (ổn định)</option>
   <option value="Declining">Declining (đi xuống)</option>
 </select>
</div>
<div class="grid">{blocks}</div>
<footer>Dashboard tương tác — số liệu khớp với notebook, file SQL và Power BI.</footer>
<script>
 const LANG = {lang[["language","signal","desired_next_year","net_change","growth_pct"]].to_dict("records")};
 function applyFilter(){{
   const s = document.getElementById('sig').value;
   const rows = (s==='all')? LANG : LANG.filter(r=>r.signal===s);
   const byDesire=[...rows].sort((a,b)=>a.desired_next_year-b.desired_next_year);
   Plotly.restyle('{ids[0]}', {{x:[byDesire.map(r=>r.desired_next_year)], y:[byDesire.map(r=>r.language)],
       text:[byDesire.map(r=>r.desired_next_year)]}});
   const byNet=[...rows].sort((a,b)=>Math.abs(a.net_change)-Math.abs(b.net_change));
   Plotly.restyle('{ids[1]}', {{x:[byNet.map(r=>r.net_change)], y:[byNet.map(r=>r.language)],
       text:[byNet.map(r=>(r.growth_pct>=0?'+':'')+Math.round(r.growth_pct)+'%')],
       'marker.color':[byNet.map(r=>r.net_change>=0?'{COL['good']}':'{COL['bad']}')]}});
 }}
</script>
</body></html>"""
    out = PBI / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"[ok] dashboard tương tác -> {out.relative_to(ROOT)}")


def main() -> None:
    tables = export_tables()
    build_dashboard(tables)
    print("HOÀN TẤT generate_deliverables.")


if __name__ == "__main__":
    main()
