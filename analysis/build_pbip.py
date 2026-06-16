"""
build_pbip.py — Sinh một Power BI Project (.pbip) TỰ CHỨA, mở là chạy.

Khác biệt then chốt: dữ liệu được NHÚNG THẲNG vào semantic model dưới dạng bảng
DAX (DATATABLE) — KHÔNG phụ thuộc file CSV bên ngoài, nên khi mở bằng Power BI
Desktop sẽ KHÔNG hỏi nguồn dữ liệu / quyền truy cập. "Bật lên là xong."

Đầu ra: powerbi/VTI_Skill_Insight.pbip  (+ thư mục .SemanticModel & .Report)

Mở: Power BI Desktop (bản 2024 trở lên) -> File -> Open -> chọn .pbip.
    (Cần bật Preview "Power BI Project (.pbip) save option" nếu Desktop hỏi.)

Chạy: python analysis/build_pbip.py
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import market_insight_data as M  # noqa: E402

NAME = "VTI_Skill_Insight"
PBI = ROOT / "powerbi"
SM = PBI / f"{NAME}.SemanticModel"
RPT = PBI / f"{NAME}.Report"

NS = uuid.UUID("12345678-1234-5678-1234-567812345678")
def guid(s: str) -> str:
    return str(uuid.uuid5(NS, s))


# -----------------------------------------------------------------------------
# TMDL: bảng dữ liệu nhúng (calculated table bằng DATATABLE)
# -----------------------------------------------------------------------------
def _col_meta(series) -> tuple[str, str, str]:
    """Suy kiểu cột từ dtype pandas -> (DATATABLE type, TMDL dataType, formatString)."""
    kind = series.dtype.kind
    if kind == "b":
        return "BOOLEAN", "boolean", ""
    if kind in ("i", "u"):
        return "INTEGER", "int64", "0"
    if kind == "f":
        return "DOUBLE", "double", "0.0"
    return "STRING", "string", ""


def _lit(v, dt_type) -> str:
    if dt_type == "STRING":
        return '"' + str(v).replace('"', '""') + '"'
    if dt_type == "BOOLEAN":
        return "TRUE" if v else "FALSE"
    if dt_type == "INTEGER":
        return str(int(v))
    return repr(float(v))


def tmdl_table(table: str, df) -> str:
    cols = list(df.columns)
    meta = {c: _col_meta(df[c]) for c in cols}

    # Khai báo cột
    lines = [f"table {table}", f"\tlineageTag: {guid('t:'+table)}", ""]
    for c in cols:
        dt_type, tmdl_dt, fmt = meta[c]
        lines.append(f"\tcolumn {c}")
        lines.append(f"\t\tdataType: {tmdl_dt}")
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append(f"\t\tlineageTag: {guid(f'c:{table}:{c}')}")
        lines.append(f"\t\tsummarizeBy: {'sum' if tmdl_dt in ('int64','double') else 'none'}")
        lines.append("\t\tisNameInferred")
        lines.append(f"\t\tsourceColumn: [{c}]")
        lines.append("")

    # Partition DATATABLE
    type_decl = ",\n\t\t\t\t".join(f'"{c}", {meta[c][0]}' for c in cols)
    rows = []
    for _, r in df.iterrows():
        vals = ", ".join(_lit(r[c], meta[c][0]) for c in cols)
        rows.append("\t\t\t\t\t{" + vals + "}")
    rows_block = ",\n".join(rows)
    lines += [
        f"\tpartition {table} = calculated",
        "\t\tmode: import",
        "\t\tsource = ```",
        "\t\t\tDATATABLE(",
        f"\t\t\t\t{type_decl},",
        "\t\t\t\t{",
        rows_block,
        "\t\t\t\t}",
        "\t\t\t)",
        "\t\t```",
        "",
    ]
    return "\n".join(lines)


def tmdl_measures() -> str:
    """Bảng chứa measure (KPI). Dùng bảng 1 dòng ẩn để gắn measure."""
    m = [
        ("Total Respondents",
         'CALCULATE(MAXX(dataset_overview, dataset_overview[value]), '
         'FILTER(dataset_overview, dataset_overview[metric] = "Total respondents"))', "#,0"),
        ("Total Countries",
         'CALCULATE(MAXX(dataset_overview, dataset_overview[value]), '
         'FILTER(dataset_overview, dataset_overview[metric] = "Countries covered"))', "0"),
        ("Median Salary USD",
         'CALCULATE(MAXX(dataset_overview, dataset_overview[value]), '
         'FILTER(dataset_overview, dataset_overview[metric] = "Median salary USD"))', "\\$#,0"),
        ("Top Desired Language",
         'MAXX(TOPN(1, ALL(language_signal), language_signal[desired_next_year], DESC), '
         'language_signal[language])', ""),
        ("Top Database",
         'MAXX(TOPN(1, ALL(database_signal), database_signal[desired_next_year], DESC), '
         'database_signal[database])', ""),
        ("Emerging Language Count",
         'CALCULATE(COUNTROWS(language_signal), language_signal[signal] = "Emerging")', "0"),
        ("Total Desired (Languages)", "SUM(language_signal[desired_next_year])", "#,0"),
        ("Median Exp Years",
         'CALCULATE(MAXX(dataset_overview, dataset_overview[value]), '
         'FILTER(dataset_overview, dataset_overview[metric] = "Median professional coding years"))', "0"),
        ("Full-time Pct",
         'CALCULATE(MAXX(dataset_overview, dataset_overview[value]), '
         'FILTER(dataset_overview, dataset_overview[metric] = "Employed full-time percentage"))', "0.0"),
        ("Avg Languages",
         'CALCULATE(MAXX(dataset_overview, dataset_overview[value]), '
         'FILTER(dataset_overview, dataset_overview[metric] = "Average languages worked per respondent"))', "0.0"),
        ("VN Total JD", "1200", "#,0"),
        ("VN Top Skill",
         'CONCATENATEX(TOPN(1, ALL(vn_itviec_skill_demand), '
         'vn_itviec_skill_demand[jobs_count], DESC), vn_itviec_skill_demand[skill], ", ")', ""),
        ("VN Public Salary Pct", "0", "0"),
    ]
    lines = ["table Measures", f"\tlineageTag: {guid('t:Measures')}", ""]
    for name, expr, fmt in m:
        lines.append(f"\tmeasure '{name}' = {expr}")
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append(f"\t\tlineageTag: {guid('m:'+name)}")
        lines.append("")
    # cột ẩn + partition rỗng
    lines += [
        "\tcolumn _hidden",
        "\t\tdataType: int64",
        "\t\tisHidden",
        f"\t\tlineageTag: {guid('c:Measures:_hidden')}",
        "\t\tsummarizeBy: none",
        "\t\tisNameInferred",
        "\t\tsourceColumn: [_hidden]",
        "",
        "\tpartition Measures = calculated",
        "\t\tmode: import",
        "\t\tsource = ```",
        '\t\t\tDATATABLE("_hidden", INTEGER, {{0}})',
        "\t\t```",
        "",
    ]
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# PBIR report: 1 trang Overview với KPI cards + 2 bar + 2 slicer
# -----------------------------------------------------------------------------
def col_field(entity, prop, ref=None):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop}}, "queryRef": ref or f"{entity}.{prop}"}


def measure_field(name):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "Measures"}},
            "Property": name}}, "queryRef": f"Measures.{name}"}


def card_visual(vid, x, y, w, h, measure_name, title):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": vid,
        "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "card",
            "query": {"queryState": {"Values": {"projections": [measure_field(measure_name)]}}},
            "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}]},
            "visualContainerObjects": {
                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                          "show": {"expr": {"Literal": {"Value": "true"}}}}}]},
            "drillFilterOtherVisuals": True,
        },
    }


def bar_visual(vid, x, y, w, h, entity, cat, val, title, is_measure=False):
    valproj = measure_field(val) if is_measure else col_field(entity, val)
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": vid,
        "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "barChart",
            "query": {"queryState": {
                "Category": {"projections": [col_field(entity, cat)]},
                "Y": {"projections": [valproj]},
            }},
            "visualContainerObjects": {
                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                          "show": {"expr": {"Literal": {"Value": "true"}}}}}]},
            "drillFilterOtherVisuals": True,
        },
    }


def column_visual(vid, x, y, w, h, entity, cat, vals, title):
    """Clustered column chart: 1 category + nhiều cột giá trị."""
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": vid,
        "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {"queryState": {
                "Category": {"projections": [col_field(entity, cat)]},
                "Y": {"projections": [col_field(entity, v) for v in vals]},
            }},
            "visualContainerObjects": {
                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                          "show": {"expr": {"Literal": {"Value": "true"}}}}}]},
            "drillFilterOtherVisuals": True,
        },
    }


def slicer_visual(vid, x, y, w, h, entity, field, title):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": vid,
        "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [col_field(entity, field)]}}},
            "visualContainerObjects": {
                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                          "show": {"expr": {"Literal": {"Value": "true"}}}}}]},
            "drillFilterOtherVisuals": True,
        },
    }


def write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def build():
    # ---- clean ----
    for d in (SM, RPT):
        if d.exists():
            import shutil
            shutil.rmtree(d)

    # ---- .pbip ----
    write(PBI / f"{NAME}.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })

    # ---- SemanticModel ----
    write(SM / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": guid("sm")},
    })
    write(SM / "definition.pbism", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {},
    })
    (SM / "definition").mkdir(parents=True, exist_ok=True)
    (SM / "definition" / "database.tmdl").write_text(
        "database\n\tcompatibilityLevel: 1567\n", encoding="utf-8")
    (SM / "definition" / "model.tmdl").write_text(
        "model Model\n"
        "\tculture: en-US\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tdiscourageImplicitMeasures\n"
        "\tsourceQueryCulture: en-US\n\n"
        "\tannotation __PBI_TimeIntelligenceEnabled = 0\n",
        encoding="utf-8")

    import pandas as pd
    vn_demand = pd.read_csv(PBI / "vn_itviec_skill_demand.csv")
    vn_cmp = pd.read_csv(PBI / "vn_vs_global_compare.csv")
    tables = {
        "dataset_overview": M.dataset_overview()[["metric", "value"]],
        "language_signal": M.language_signal(),
        "database_signal": M.database_signal(),
        "ide_overall": M.ide_overall(),
        "salary_by_language": M.salary_by_language(),
        "role_priority": M.role_priority(),
        "country_distribution": M.country_distribution(),
        "interview_rubric": M.interview_rubric()[["assessment_area", "weight_pct"]],
        "vn_itviec_skill_demand": vn_demand,
        "vn_vs_global_compare": vn_cmp,
    }
    tdir = SM / "definition" / "tables"
    tdir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        (tdir / f"{name}.tmdl").write_text(tmdl_table(name, df), encoding="utf-8")
    (tdir / "Measures.tmdl").write_text(tmdl_measures(), encoding="utf-8")

    # ---- Report ----
    write(RPT / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": guid("rpt")},
    })
    write(RPT / "definition.pbir", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}, "byConnection": None},
    })
    rdef = RPT / "definition"
    write(rdef / "report.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/2.0.0/schema.json",
        "themeCollection": {"baseTheme": {"name": "CY24SU10"}},
        "layoutOptimization": "None",
    })

    # ---- 4 trang theo thiết kế handoff ----
    pages = [
        ("overview", "01 · Tổng quan", [
            card_visual("o_k1", 16, 16, 200, 96, "Total Respondents", "Developers"),
            card_visual("o_k2", 224, 16, 200, 96, "Total Countries", "Quốc gia"),
            card_visual("o_k3", 432, 16, 200, 96, "Median Salary USD", "Median salary"),
            card_visual("o_k4", 640, 16, 200, 96, "Median Exp Years", "Kinh nghiệm (năm)"),
            card_visual("o_k5", 848, 16, 200, 96, "Full-time Pct", "Full-time %"),
            card_visual("o_k6", 1056, 16, 208, 96, "Avg Languages", "Ngôn ngữ/dev"),
            slicer_visual("o_slc", 16, 124, 1248, 64, "language_signal", "signal", "Bộ lọc tín hiệu"),
            bar_visual("o_worked", 16, 200, 412, 360, "language_signal", "language",
                       "worked", "Ngôn ngữ · đang dùng"),
            bar_visual("o_desired", 436, 200, 412, 360, "language_signal", "language",
                       "desired_next_year", "Ngôn ngữ · mong muốn năm tới"),
            bar_visual("o_country", 856, 200, 408, 360, "country_distribution", "country",
                       "pct", "Phân bố nhà phát triển theo quốc gia (%)"),
        ]),
        ("demand", "02 · Cung–cầu kỹ năng", [
            column_visual("d_db", 16, 16, 624, 330, "database_signal", "database",
                          ["worked", "desired_next_year"], "Database: đang dùng vs muốn dùng"),
            bar_visual("d_gap", 656, 16, 608, 330, "database_signal", "database",
                       "net_change", "Skill-gap database (net change)"),
            bar_visual("d_sal", 16, 360, 412, 344, "salary_by_language", "language",
                       "median_salary", "Lương trung vị theo ngôn ngữ (USD)"),
            bar_visual("d_ide", 436, 360, 412, 344, "ide_overall", "ide",
                       "usage_pct", "IDE phổ biến nhất (%)"),
            bar_visual("d_iderole", 856, 360, 408, 344, "role_priority", "role",
                       "developer_count", "Quy mô theo vai trò (số dev)"),
        ]),
        ("vietnam", "03 · Việt Nam · ItViec", [
            card_visual("v_k1", 16, 16, 300, 96, "VN Total JD", "Tin tuyển dụng (ItViec)"),
            card_visual("v_k2", 324, 16, 300, 96, "VN Top Skill", "Kỹ năng kỹ thuật #1"),
            card_visual("v_k3", 632, 16, 300, 96, "VN Public Salary Pct", "% JD công khai lương"),
            card_visual("v_k4", 940, 16, 324, 96, "Median Salary USD", "Mốc lương toàn cầu"),
            bar_visual("v_demand", 16, 124, 624, 444, "vn_itviec_skill_demand", "skill",
                       "pct_of_jobs", "Cầu kỹ năng tại Việt Nam (% trên 1.200 JD)"),
            column_visual("v_cmp", 656, 124, 608, 444, "vn_vs_global_compare", "vn_skill",
                          ["vn_pct_of_jd"], "Top kỹ năng VN (% JD) — đối chiếu toàn cầu"),
        ]),
        ("strategy", "04 · Khuyến nghị", [
            bar_visual("s_role", 16, 16, 624, 344, "role_priority", "role",
                       "hiring_priority_score", "Ưu tiên tuyển dụng theo vai trò (điểm)"),
            bar_visual("s_emerging", 656, 16, 608, 344, "language_signal", "language",
                       "growth_pct", "Tăng trưởng nhu cầu ngôn ngữ (%)"),
            bar_visual("s_rubric", 16, 376, 624, 328, "interview_rubric", "assessment_area",
                       "weight_pct", "Khung chấm phỏng vấn (trọng số %)"),
            bar_visual("s_emerging_db", 656, 376, 608, 328, "database_signal", "database",
                       "growth_pct", "Tăng trưởng nhu cầu database (%)"),
        ]),
    ]

    page_ids = [p[0] for p in pages]
    write(rdef / "pages" / "pages.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": page_ids, "activePageName": page_ids[0],
    })
    total_visuals = 0
    for pid, disp, visuals in pages:
        write(rdef / "pages" / pid / "page.json", {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
            "name": pid, "displayName": disp,
            "displayOption": "FitToPage", "height": 720, "width": 1280,
        })
        for v in visuals:
            write(rdef / "pages" / pid / "visuals" / v["name"] / "visual.json", v)
            total_visuals += 1

    print(f"[ok] PBIP -> {(PBI / (NAME + '.pbip')).relative_to(ROOT)}")
    print(f"     tables: {len(tables)+1} (data nhúng) · pages: {len(pages)} · visuals: {total_visuals}")


if __name__ == "__main__":
    build()
