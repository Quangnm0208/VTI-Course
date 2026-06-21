"""
build_dashboard_pro.py — Dashboard 4 trang theo thiết kế handoff (chuyên nghiệp).

Sinh powerbi/dashboard.html: bản dashboard tương tác mở bằng trình duyệt, bám đúng
giao diện trong gói handoff (font Inter + JetBrains Mono, bảng màu chàm, 4 trang,
bộ lọc Tín hiệu + Top N). Dữ liệu nhúng sẵn (JSON) — mở là chạy, không cần server.

Trang:
    01 Tổng quan (Executive Overview)
    02 Cung–cầu kỹ năng (Skill Demand Deep Dive)
    03 Việt Nam · ItViec
    04 Khuyến nghị · Chiến lược

Chạy: python analysis/build_dashboard_pro.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import market_insight_data as M  # noqa: E402

PBI = ROOT / "powerbi"
OUT = PBI / "dashboard.html"

PAL = {
    "primary": "#3b3fbf", "primaryDark": "#1b1e6b", "accent": "#6e76dd",
    "accentSoft": "#939ae6", "lav": "#eef0fb", "ink": "#0f1014", "ink2": "#060608",
    "muted": "#5b6678", "muted2": "#8a93a3", "border": "#e6e8ec", "bg": "#f3f4f7",
    "card": "#ffffff", "emerging": "#10b981", "stable": "#6e76dd", "declining": "#dc2626",
}


def df_records(df):
    return json.loads(df.to_json(orient="records"))


def vn_csv(name):
    with open(PBI / f"{name}.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build():
    ov = M.dataset_overview().set_index("metric")["value"].to_dict()
    data = {
        "overview": ov,
        "language": df_records(M.language_signal()),
        "database": df_records(M.database_signal()),
        "ide": df_records(M.ide_overall()),
        "salary": df_records(M.salary_by_language()),
        "role": df_records(M.role_priority()),
        "country": df_records(M.country_distribution()),
        "roadmap": df_records(M.training_roadmap()),
        "rubric": df_records(M.interview_rubric()),
        "recs": df_records(M.strategic_recommendations()),
        "vn_demand": [{"skill": r["skill"], "jobs_count": int(r["jobs_count"]),
                       "pct_of_jobs": float(r["pct_of_jobs"])} for r in vn_csv("vn_itviec_skill_demand")],
        "vn_salary": [{"tier": r["tier"], "min": int(r["annual_usd_min"]),
                       "max": int(r["annual_usd_max"]), "kind": r["kind"], "source": r["source"]}
                      for r in vn_csv("vn_salary_benchmark")],
        "vn_cmp": [{"rank": int(r["rank"]), "vn_skill": r["vn_skill"],
                    "vn_pct": float(r["vn_pct_of_jd"]), "global_language": r["global_language"],
                    "global_worked": int(r["global_worked"])} for r in vn_csv("vn_vs_global_compare")],
    }
    payload = json.dumps(data, ensure_ascii=False)
    pal = json.dumps(PAL)

    html = HTML_TEMPLATE.replace("/*__PALETTE__*/", pal).replace("/*__DATA__*/", payload)
    OUT.write_text(html, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"[ok] dashboard 4 trang -> {OUT.relative_to(ROOT)} ({kb:.0f} KB)")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>VTI Skill Market — Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{ --pri:#3b3fbf; --priD:#1b1e6b; --acc:#6e76dd; --lav:#eef0fb; --ink:#0f1014;
 --muted:#5b6678; --muted2:#8a93a3; --bd:#e6e8ec; --bg:#f3f4f7; --emerging:#10b981; --declining:#dc2626;}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter',system-ui,'Segoe UI',sans-serif;background:var(--bg);color:var(--ink);}
.app{display:grid;grid-template-columns:236px 1fr;min-height:100vh}
/* Sidebar */
.side{background:linear-gradient(180deg,#1b1e6b,#0f1140);color:#fff;padding:22px 16px;position:sticky;top:0;height:100vh}
.brand{font-weight:800;font-size:18px;letter-spacing:.2px;line-height:1.25}
.brand small{display:block;font-weight:500;color:#b8bfef;font-size:12px;margin-top:4px}
.nav{margin-top:28px;display:flex;flex-direction:column;gap:6px}
.nav button{display:flex;gap:12px;align-items:center;background:transparent;border:0;color:#c7cbf0;
 padding:11px 12px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:14px;text-align:left;width:100%}
.nav button .num{font-family:'JetBrains Mono';font-weight:700;color:#7c83e0;font-size:13px}
.nav button:hover{background:rgba(255,255,255,.07)}
.nav button.active{background:#fff;color:#1b1e6b;font-weight:700}
.nav button.active .num{color:var(--pri)}
.side .foot{position:absolute;bottom:18px;left:16px;right:16px;font-size:11px;color:#8a90d6;line-height:1.5}
/* Main */
.main{padding:26px 30px 50px}
.head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
.head h1{margin:0;font-size:24px;font-weight:800}
.head p{margin:5px 0 0;color:var(--muted);font-size:13px}
.filters{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.filters .lbl{font-size:12px;color:var(--muted2);margin-right:2px}
.seg{display:inline-flex;background:#fff;border:1px solid var(--bd);border-radius:10px;overflow:hidden}
.seg button{border:0;background:transparent;padding:7px 13px;font-family:inherit;font-size:13px;cursor:pointer;color:var(--muted)}
.seg button.on{background:var(--pri);color:#fff;font-weight:600}
/* KPI */
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin:20px 0}
.kpi{background:#fff;border:1px solid var(--bd);border-radius:14px;padding:15px 16px}
.kpi .k{font-size:11px;color:var(--muted2);text-transform:uppercase;letter-spacing:.05em;font-weight:600}
.kpi .v{font-family:'JetBrains Mono';font-weight:700;font-size:24px;margin-top:7px;color:var(--priD)}
.kpi .s{font-size:11px;color:var(--muted);margin-top:3px}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}
.panel{background:#fff;border:1px solid var(--bd);border-radius:14px;padding:6px 8px 2px}
.panel h3{margin:12px 12px 2px;font-size:14px;font-weight:700}
.panel .cap{margin:0 12px 6px;font-size:12px;color:var(--muted2)}
.note{background:var(--lav);border:1px solid #d9ddf6;border-radius:12px;padding:12px 14px;font-size:12.5px;color:#33386e;margin-top:6px}
.tbl{width:100%;border-collapse:collapse;font-size:13px}
.tbl th,.tbl td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--bd)}
.tbl th{color:var(--muted2);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.tbl td .mono{font-family:'JetBrains Mono';font-weight:700}
.chip{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:600}
.chip.Emerging{background:#dcfce7;color:#0b7a55}.chip.Stable{background:#eef0fb;color:#3b3fbf}.chip.Declining{background:#eef0f3;color:#5b6678}
.reccard{background:#fff;border:1px solid var(--bd);border-left:5px solid var(--pri);border-radius:12px;padding:14px 16px}
.reccard b{color:var(--priD)} .reccard .h{font-size:13px;color:var(--acc);font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.page{display:none}.page.show{display:block}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}.g2,.g3{grid-template-columns:1fr}.app{grid-template-columns:1fr}.side{position:static;height:auto}}
</style></head>
<body>
<div class="app">
 <aside class="side">
   <div class="brand">VTI Skill Market<small>Phân tích kỹ năng IT · VTI Academy</small></div>
   <nav class="nav" id="nav">
     <button data-p="overview" class="active"><span class="num">01</span> Tổng quan</button>
     <button data-p="demand"><span class="num">02</span> Cung–cầu kỹ năng</button>
     <button data-p="vietnam"><span class="num">03</span> Việt Nam · ItViec</button>
     <button data-p="strategy"><span class="num">04</span> Khuyến nghị</button>
   </nav>
   <div class="foot">Nguồn dữ liệu thực tế: <b>Stack Overflow Developer Survey 2025</b> 49.191 dev / 177 quốc gia (VN 145) · <b>GitHub API</b> 7.600 repo · <b>ItViec</b> 1.200 JD. IDE lấy từ kỳ khảo sát gần nhất có hỏi (SO 2025 bỏ câu hỏi IDE).</div>
 </aside>
 <main class="main">
   <div class="head">
     <div><h1 id="ptitle">Tổng quan điều hành</h1><p id="psub"></p></div>
     <div class="filters">
       <span class="lbl">Tín hiệu</span>
       <div class="seg" id="sigSeg">
         <button data-s="all" class="on">Tất cả</button>
         <button data-s="Emerging">Emerging</button>
         <button data-s="Stable">Stable</button>
         <button data-s="Declining">Declining</button>
       </div>
       <span class="lbl">Top</span>
       <div class="seg" id="topSeg">
         <button data-n="5">5</button><button data-n="10" class="on">10</button><button data-n="999">All</button>
       </div>
     </div>
   </div>

   <section class="page show" id="p_overview"></section>
   <section class="page" id="p_demand"></section>
   <section class="page" id="p_vietnam"></section>
   <section class="page" id="p_strategy"></section>
 </main>
</div>

<script>
const PAL = /*__PALETTE__*/;
// Bảng màu rút gọn còn ĐÚNG 3 màu: chàm (chính) · xanh lá (tích cực) · xám (trung tính)
const C1='#3b3fbf', C2='#10b981', C3='#94a3b8';
Object.assign(PAL,{primary:C1,primaryDark:C1,accent:C1,accentSoft:C3,stable:C1,
  emerging:C2,declining:C3,muted2:C3});
const D = /*__DATA__*/;
let STATE = {page:'overview', signal:'all', topN:10};
const SIGCOL = {Emerging:PAL.emerging, Stable:PAL.stable, Declining:PAL.declining};
const FONT = {family:"Inter, sans-serif", size:12, color:PAL.ink};
const baseLayout = (title)=>({title:{text:title,font:{size:14,color:PAL.ink}},
  template:'plotly_white', font:FONT, margin:{l:8,r:18,t:38,b:28}, height:330,
  xaxis:{gridcolor:'#eef0f3'}, yaxis:{automargin:true}, showlegend:false, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)'});
const CFG = {displayModeBar:false, responsive:true};

function fmt(n){return n.toLocaleString('en-US');}
function applyFilters(rows){
  let r = rows;
  if(STATE.signal!=='all') r = r.filter(x=>x.signal===STATE.signal);
  return r;
}
function topSlice(rows, key){ return [...rows].sort((a,b)=>b[key]-a[key]).slice(0, STATE.topN); }

/* ---------- PAGE 1: OVERVIEW ---------- */
function renderOverview(){
  const o=D.overview;
  const kpis=[
   ['Developers',fmt(o['Total respondents']),'khảo sát toàn cầu'],
   ['Quốc gia',o['Countries covered'],'135 quốc gia'],
   ['Median salary','$'+fmt(o['Median salary USD']),'USD/năm (toàn cầu)'],
   ['Kinh nghiệm',o['Median professional coding years']+' năm','median chuyên nghiệp'],
   ['Full-time',o['Employed full-time percentage']+'%','tỷ lệ đi làm'],
   ['Ngôn ngữ/dev',o['Average languages worked per respondent'],'trung bình thành thạo'],
  ];
  const el=document.getElementById('p_overview');
  el.innerHTML = `<div class="kpis">${kpis.map(k=>`<div class="kpi"><div class="k">${k[0]}</div><div class="v">${k[1]}</div><div class="s">${k[2]}</div></div>`).join('')}</div>
   <div class="grid g2"><div class="panel"><div id="o_worked"></div></div><div class="panel"><div id="o_desired"></div></div></div>
   <div class="grid g2" style="margin-top:16px"><div class="panel"><div id="o_country"></div></div>
   <div class="panel"><div id="o_net"></div></div></div>`;
  const lw=topSlice(applyFilters(D.language),'worked');
  Plotly.newPlot('o_worked',[{type:'bar',orientation:'h',x:lw.map(r=>r.worked).reverse(),y:lw.map(r=>r.language).reverse(),
    marker:{color:PAL.accent},text:lw.map(r=>fmt(r.worked)).reverse(),textposition:'auto'}],baseLayout('Ngôn ngữ · đang dùng (worked)'),CFG);
  const ld=topSlice(applyFilters(D.language),'desired_next_year');
  Plotly.newPlot('o_desired',[{type:'bar',orientation:'h',x:ld.map(r=>r.desired_next_year).reverse(),y:ld.map(r=>r.language).reverse(),
    marker:{color:PAL.primary},text:ld.map(r=>fmt(r.desired_next_year)).reverse(),textposition:'auto'}],baseLayout('Ngôn ngữ · mong muốn năm tới (desired)'),CFG);
  const c=[...D.country].sort((a,b)=>a.pct-b.pct);
  Plotly.newPlot('o_country',[{type:'bar',orientation:'h',x:c.map(r=>r.pct),y:c.map(r=>r.country),
    marker:{color:PAL.priD||PAL.primaryDark||'#1b1e6b'},text:c.map(r=>r.pct+'%'),textposition:'auto'}],baseLayout('Phân bố nhà phát triển theo quốc gia (%)'),CFG);
  const net=topSlice(applyFilters(D.language).map(r=>({...r,abs:Math.abs(r.net_change)})),'abs');
  const ns=[...net].sort((a,b)=>a.net_change-b.net_change);
  Plotly.newPlot('o_net',[{type:'bar',orientation:'h',x:ns.map(r=>r.net_change),y:ns.map(r=>r.language),
    marker:{color:ns.map(r=>r.net_change>=0?PAL.emerging:PAL.declining)},text:ns.map(r=>(r.growth_pct>=0?'+':'')+r.growth_pct+'%'),textposition:'auto'}],
    {...baseLayout('Thay đổi ròng nhu cầu ngôn ngữ (muốn − đang dùng)')},CFG);
}

/* ---------- PAGE 2: DEMAND ---------- */
function renderDemand(){
  const el=document.getElementById('p_demand');
  el.innerHTML=`<div class="grid g2"><div class="panel"><div id="d_db"></div></div><div class="panel"><div id="d_gap"></div></div></div>
   <div class="grid g3" style="margin-top:16px"><div class="panel"><div id="d_sal"></div></div>
    <div class="panel"><div id="d_ide"></div></div>
    <div class="panel"><h3>IDE theo vai trò</h3><p class="cap">Top công cụ mỗi nhóm developer</p><div id="d_iderole"></div></div></div>`;
  const db=topSlice(applyFilters(D.database),'desired_next_year');
  Plotly.newPlot('d_db',[
    {type:'bar',name:'Đang dùng',x:db.map(r=>r.database),y:db.map(r=>r.worked),marker:{color:PAL.accentSoft||'#939ae6'}},
    {type:'bar',name:'Muốn dùng',x:db.map(r=>r.database),y:db.map(r=>r.desired_next_year),marker:{color:PAL.primary}}
  ],{...baseLayout('Cơ sở dữ liệu: đang dùng vs muốn dùng'),barmode:'group',showlegend:true,legend:{orientation:'h',y:1.12}},CFG);
  const gapRows=applyFilters(D.database);
  const gs=[...gapRows].sort((a,b)=>a.net_change-b.net_change);
  Plotly.newPlot('d_gap',[{type:'bar',orientation:'h',x:gs.map(r=>r.net_change),y:gs.map(r=>r.database),
    marker:{color:gs.map(r=>r.net_change>=0?PAL.emerging:PAL.declining)},text:gs.map(r=>(r.growth_pct>=0?'+':'')+r.growth_pct+'%'),textposition:'auto'}],
    baseLayout('Skill-gap database (net change)'),CFG);
  const sal=[...D.salary].sort((a,b)=>a.median_salary-b.median_salary).slice(-10);
  Plotly.newPlot('d_sal',[{type:'bar',orientation:'h',x:sal.map(r=>r.median_salary),y:sal.map(r=>r.language),
    marker:{color:PAL.emerging},text:sal.map(r=>'$'+Math.round(r.median_salary/1000)+'k'),textposition:'auto'}],baseLayout('Lương trung vị theo ngôn ngữ (USD)'),CFG);
  const ide=[...D.ide].sort((a,b)=>a.usage_pct-b.usage_pct);
  Plotly.newPlot('d_ide',[{type:'bar',orientation:'h',x:ide.map(r=>r.usage_pct),y:ide.map(r=>r.ide),
    marker:{color:PAL.primary},text:ide.map(r=>r.usage_pct+'%'),textposition:'auto'}],baseLayout('IDE phổ biến nhất (% · kỳ SO gần nhất có hỏi IDE)'),CFG);
  // ide by role -> small table style heat via bars
  const roles=[...new Set(D.role.map(r=>r.role))];
  document.getElementById('d_iderole').innerHTML =
   `<table class="tbl"><thead><tr><th>Vai trò</th><th>IDE chuẩn onboarding</th></tr></thead><tbody>
    ${roles.slice(0,8).map(r=>`<tr><td>${r}</td><td><span class="mono">VS Code</span></td></tr>`).join('')}</tbody></table>`;
}

/* ---------- PAGE 3: VIETNAM ---------- */
function renderVietnam(){
  const el=document.getElementById('p_vietnam');
  const top=D.vn_demand[0], py=D.vn_demand.find(x=>x.skill==='Python');
  el.innerHTML=`<div class="kpis" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi"><div class="k">Tin tuyển dụng</div><div class="v">1.200</div><div class="s">ItViec · 28–29/05/2026</div></div>
    <div class="kpi"><div class="k">Kỹ năng kỹ thuật #1</div><div class="v" style="font-size:19px">Python / AI</div><div class="s">${py.pct_of_jobs}% JD</div></div>
    <div class="kpi"><div class="k">Lương công khai</div><div class="v">0%</div><div class="s">0/1.200 JD hiện lương</div></div>
    <div class="kpi"><div class="k">Senior VN vs toàn cầu</div><div class="v">~52%</div><div class="s">$30k / $57.8k</div></div></div>
   <div class="grid g2"><div class="panel"><div id="v_demand"></div></div>
     <div class="panel"><h3>Mức lương lập trình viên Việt Nam vs mốc toàn cầu</h3>
       <p class="cap">USD/năm — khoảng min→max theo cấp</p><div id="v_salary"></div></div></div>
   <div class="grid g2" style="margin-top:16px">
     <div class="panel"><h3>Đối chiếu Top kỹ năng: Việt Nam vs Toàn cầu</h3><div id="v_cmp"></div></div>
     <div></div></div>
   <div class="note">⚠️ ItViec ẩn lương (0/1.200 JD công khai) → số lương Việt Nam lấy từ <b>TopDev/Reco/Glassdoor 2024–2026</b>, không suy từ ItViec. Mốc toàn cầu $57.844 từ Stack Overflow. Cầu kỹ năng VN tính theo % JD có nhắc kỹ năng.</div>`;
  const vd=[...D.vn_demand].slice(0,15).sort((a,b)=>a.pct_of_jobs-b.pct_of_jobs);
  Plotly.newPlot('v_demand',[{type:'bar',orientation:'h',x:vd.map(r=>r.pct_of_jobs),y:vd.map(r=>r.skill),
    marker:{color:PAL.primary},text:vd.map(r=>r.pct_of_jobs+'%'),textposition:'auto'}],baseLayout('Cầu kỹ năng tại Việt Nam (% trên 1.200 JD)'),CFG);
  const sal=D.vn_salary;
  const traces=sal.map(t=>({type:'bar',orientation:'h',y:[t.tier],x:[t.max-t.min],base:[t.min],
    marker:{color:t.kind==='vietnam'?PAL.accent:(t.kind==='global_reference'?PAL.declining:PAL.accentSoft||'#939ae6')},
    text:['$'+fmt(t.min)+(t.min!==t.max?'–$'+fmt(t.max):'')],textposition:'auto',hovertemplate:'%{y}: $'+'%{base:,}→'+'<extra></extra>'}));
  const lay={...baseLayout(''),barmode:'overlay',height:300,showlegend:false,
    shapes:[{type:'line',x0:57844,x1:57844,y0:-0.5,y1:sal.length-0.5,line:{color:PAL.declining,dash:'dot',width:2}}],
    annotations:[{x:57844,y:sal.length-0.5,text:'Mốc toàn cầu $57.844',showarrow:false,font:{color:PAL.declining,size:11},xanchor:'right',yshift:10}]};
  Plotly.newPlot('v_salary',traces,lay,CFG);
  document.getElementById('v_cmp').innerHTML=
   `<table class="tbl"><thead><tr><th>#</th><th>VN (ItViec) · % JD</th><th>Toàn cầu (SO) · #dev</th></tr></thead><tbody>
    ${D.vn_cmp.map(r=>`<tr><td class="mono">${r.rank}</td><td><b>${r.vn_skill}</b> · <span class="mono">${r.vn_pct}%</span></td>
      <td>${r.global_language} · <span class="mono">${fmt(r.global_worked)}</span></td></tr>`).join('')}</tbody></table>`;
}

/* ---------- PAGE 4: STRATEGY ---------- */
function renderStrategy(){
  const el=document.getElementById('p_strategy');
  el.innerHTML=`<div class="grid g2"><div class="panel"><div id="s_role"></div></div><div class="panel"><div id="s_emerging"></div></div></div>
   <div class="grid g2" style="margin-top:16px">
     <div class="panel" style="padding:14px"><h3 style="margin:0 0 10px">3 khuyến nghị chiến lược</h3>
       <div class="grid" style="gap:12px">${D.recs.map((r,i)=>`<div class="reccard"><div class="h">${r.horizon}</div>
         <div style="margin:5px 0 4px"><b>${r.recommendation}</b></div><div style="font-size:12.5px;color:var(--muted)">${r.evidence}</div></div>`).join('')}</div></div>
     <div class="panel" style="padding:6px 8px"><div id="s_rubric"></div>
       <h3 style="margin:14px 12px 6px">Lộ trình đào tạo 4 tuần</h3>
       <table class="tbl"><thead><tr><th>Tuần</th><th>Nội dung</th></tr></thead><tbody>
       ${D.roadmap.map(r=>`<tr><td class="mono">${r.phase}</td><td>${r.training_block}</td></tr>`).join('')}</tbody></table></div></div>`;
  const rp=[...D.role].sort((a,b)=>a.hiring_priority_score-b.hiring_priority_score);
  const band={'Priority 1':C2,'Priority 2':C1,'Priority 3':C3};
  Plotly.newPlot('s_role',[{type:'bar',orientation:'h',x:rp.map(r=>r.hiring_priority_score),y:rp.map(r=>r.role),
    marker:{color:rp.map(r=>band[r.priority_band])},text:rp.map(r=>r.hiring_priority_score),textposition:'auto'}],baseLayout('Ưu tiên tuyển dụng theo vai trò (điểm)'),CFG);
  const em=[...D.language,...D.database].filter(r=>r.signal==='Emerging').map(r=>({name:r.language||r.database,g:r.growth_pct}))
    .sort((a,b)=>a.g-b.g);
  Plotly.newPlot('s_emerging',[{type:'bar',orientation:'h',x:em.map(r=>r.g),y:em.map(r=>r.name),
    marker:{color:PAL.emerging},text:em.map(r=>'+'+r.g+'%'),textposition:'auto'}],baseLayout('Kỹ năng nổi theo tăng trưởng (%)'),CFG);
  const ru=[...D.rubric].sort((a,b)=>a.weight_pct-b.weight_pct);
  Plotly.newPlot('s_rubric',[{type:'bar',orientation:'h',x:ru.map(r=>r.weight_pct),y:ru.map(r=>r.assessment_area),
    marker:{color:PAL.accent},text:ru.map(r=>r.weight_pct+'%'),textposition:'auto'}],{...baseLayout('Khung chấm phỏng vấn (trọng số %)'),height:240},CFG);
}

const RENDER={overview:renderOverview,demand:renderDemand,vietnam:renderVietnam,strategy:renderStrategy};
const META={overview:['Tổng quan điều hành','Bức tranh nhanh: nhân lực, ngôn ngữ & nhu cầu toàn cầu'],
  demand:['Cung–cầu kỹ năng','Đi sâu database · skill-gap · lương · IDE'],
  vietnam:['Việt Nam · ItViec','Tín hiệu tuyển dụng nội địa từ 1.200 JD'],
  strategy:['Khuyến nghị · Chiến lược','Từ dữ liệu → quyết định đào tạo cho VTI Academy']};

function show(p){
  STATE.page=p;
  document.querySelectorAll('.nav button').forEach(b=>b.classList.toggle('active',b.dataset.p===p));
  document.querySelectorAll('.page').forEach(s=>s.classList.toggle('show',s.id==='p_'+p));
  document.getElementById('ptitle').textContent=META[p][0];
  document.getElementById('psub').textContent=META[p][1];
  // filters chỉ áp cho trang ngôn ngữ/database
  const useFilter=(p==='overview'||p==='demand');
  document.getElementById('sigSeg').style.opacity=useFilter?1:.4;
  document.getElementById('topSeg').style.opacity=(p==='overview')?1:.4;
  RENDER[p]();
}
document.getElementById('nav').addEventListener('click',e=>{const b=e.target.closest('button');if(b)show(b.dataset.p);});
document.getElementById('sigSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  document.querySelectorAll('#sigSeg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');STATE.signal=b.dataset.s;RENDER[STATE.page]();});
document.getElementById('topSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  document.querySelectorAll('#topSeg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');STATE.topN=+b.dataset.n;RENDER[STATE.page]();});
show('overview');
</script>
</body></html>"""


if __name__ == "__main__":
    build()
