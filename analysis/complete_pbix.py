"""
complete_pbix.py — Chèn report 4 trang vào VTI.pbix (model đã có sẵn data).

- Đọc .pbix nguồn, GIỮ NGUYÊN mọi part (đặc biệt DataModel nhị phân).
- Chỉ thay Report/Layout bằng layout mới có visual (định dạng classic .pbix).
- Card KPI lấy từ dataset_overview + filter theo metric (không cần tạo measure).
- Xuất ra VTI_completed.pbix.
"""
import json, zipfile, uuid, sys, shutil

SRC = sys.argv[1] if len(sys.argv) > 1 else "VTI.pbix"
OUT = sys.argv[2] if len(sys.argv) > 2 else "VTI_completed.pbix"
NS = uuid.UUID("12345678-1234-5678-1234-567812345678")
def gid(s): return uuid.uuid5(NS, s).hex

# Aggregation Function: 0=Sum, 4=Max
def col(src, prop):
    return {"Column": {"Expression": {"SourceRef": {"Source": src}}, "Property": prop}}
def agg(src, prop, fn=0):
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": src}}, "Property": prop}}, "Function": fn}}

def title_obj(text):
    return {"title": [{"properties": {
        "text": {"expr": {"Literal": {"Value": "'%s'" % text.replace("'", " ")}}},
        "show": {"expr": {"Literal": {"Value": "true"}}}}}]}

def vc(vid, x, y, w, h, vtype, entity, title, cats=None, vals=None,
       agg_fn=0, order_desc_on=None, table_cols=None, card_metric=None, z=0):
    """Tạo 1 visualContainer classic."""
    src = entity[:2]
    select, projections = [], {}
    if card_metric is not None:
        # Card: Sum(value) + filter metric
        a = agg(src, "value", 0); a["Name"] = "Sum(%s.value)" % entity
        select.append(a)
        projections = {"Values": [{"queryRef": "Sum(%s.value)" % entity}]}
    elif table_cols:
        for c in table_cols:
            cc = col(src, c); cc["Name"] = "%s.%s" % (entity, c)
            select.append(cc)
        projections = {"Values": [{"queryRef": "%s.%s" % (entity, c)} for c in table_cols]}
    elif vtype == "slicer":
        cc = col(src, cats[0]); cc["Name"] = "%s.%s" % (entity, cats[0])
        select.append(cc)
        projections = {"Values": [{"queryRef": "%s.%s" % (entity, cats[0])}]}
    else:
        # chart: category + 1..n value (Sum)
        cc = col(src, cats[0]); cc["Name"] = "%s.%s" % (entity, cats[0])
        select.append(cc)
        catrole = "Category" if vtype != "clusteredColumnChart" else "Category"
        projections[catrole] = [{"queryRef": "%s.%s" % (entity, cats[0])}]
        yrefs = []
        for v in vals:
            a = agg(src, v, agg_fn); a["Name"] = "Sum(%s.%s)" % (entity, v)
            select.append(a); yrefs.append({"queryRef": "Sum(%s.%s)" % (entity, v)})
        projections["Y"] = yrefs

    proto = {"Version": 2, "From": [{"Name": src, "Entity": entity, "Type": 0}], "Select": select}
    if order_desc_on:
        proto["OrderBy"] = [{"Direction": 2,
                             "Expression": {"Aggregation": agg(src, order_desc_on, agg_fn)["Aggregation"]}}]

    config = {
        "name": gid(vid),
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z}}],
        "singleVisual": {
            "visualType": vtype,
            "projections": projections,
            "prototypeQuery": proto,
            "drillFilterOtherVisuals": True,
            "objects": {},
            "vcObjects": {"title": title_obj(title)["title"]},
        },
    }
    filters = "[]"
    if card_metric is not None:
        filters = json.dumps([{
            "name": gid(vid + "f"),
            "expression": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": "metric"}},
            "filter": {"Version": 2, "From": [{"Name": src, "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {
                           "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": src}}, "Property": "metric"}}],
                           "Values": [[{"Literal": {"Value": "'%s'" % card_metric}}]]}}}]},
            "type": "Categorical"}])
    return {"x": x, "y": y, "z": z, "width": w, "height": h,
            "config": json.dumps(config), "filters": filters,
            "queryHash": 0}

def page(name, disp, ordinal, vlist):
    return {"id": ordinal, "name": gid(name)[:20], "displayName": disp,
            "filters": "[]", "ordinal": ordinal, "visualContainers": vlist,
            "config": "{}", "displayOption": 1, "width": 1280, "height": 720}

# ---------- Định nghĩa 4 trang ----------
p1 = [
    vc("k1", 16, 12, 232, 96, "card", "dataset_overview", "Developers", card_metric="Total respondents"),
    vc("k2", 256, 12, 232, 96, "card", "dataset_overview", "Quoc gia", card_metric="Countries covered"),
    vc("k3", 496, 12, 232, 96, "card", "dataset_overview", "Median salary USD", card_metric="Median salary USD"),
    vc("k4", 736, 12, 250, 96, "card", "dataset_overview", "Kinh nghiem (nam)", card_metric="Median professional coding years"),
    vc("k5", 996, 12, 268, 96, "card", "dataset_overview", "Full-time %", card_metric="Employed full-time percentage"),
    vc("lw", 16, 120, 408, 300, "clusteredBarChart", "language_signal", "Ngon ngu dang dung",
       cats=["language"], vals=["worked"], order_desc_on="worked"),
    vc("ld", 432, 120, 408, 300, "clusteredBarChart", "language_signal", "Ngon ngu muon dung nam toi",
       cats=["language"], vals=["desired_next_year"], order_desc_on="desired_next_year"),
    vc("ct", 848, 120, 416, 300, "clusteredColumnChart", "country_distribution", "Top quoc gia (%)",
       cats=["country"], vals=["pct"], order_desc_on="pct"),
    vc("s1", 16, 432, 280, 272, "slicer", "language_signal", "Loc: Tin hieu", cats=["signal"]),
    vc("s2", 312, 432, 280, 272, "slicer", "role_priority", "Loc: Nhom uu tien", cats=["priority_band"]),
    vc("sal1", 608, 432, 656, 272, "clusteredBarChart", "salary_by_language", "Luong trung vi theo ngon ngu (USD)",
       cats=["language"], vals=["median_salary"], order_desc_on="median_salary"),
]
p2 = [
    vc("db", 16, 16, 624, 340, "clusteredColumnChart", "database_signal", "Database: dang dung vs muon dung",
       cats=["database"], vals=["worked", "desired_next_year"], order_desc_on="desired_next_year"),
    vc("gap", 656, 16, 608, 340, "clusteredBarChart", "language_signal", "Skill-gap ngon ngu (net change)",
       cats=["language"], vals=["net_change"], order_desc_on="net_change"),
    vc("ide", 16, 372, 624, 332, "clusteredBarChart", "ide_overall", "IDE pho bien (%)",
       cats=["ide"], vals=["usage_pct"], order_desc_on="usage_pct"),
    vc("role", 656, 372, 608, 332, "clusteredBarChart", "role_priority", "Uu tien tuyen dung theo vai tro",
       cats=["role"], vals=["hiring_priority_score"], order_desc_on="hiring_priority_score"),
]
p3 = [
    vc("vnd", 16, 16, 624, 688, "clusteredBarChart", "vn_itviec_skill_demand", "Cau ky nang tai Viet Nam (% tren 1200 JD)",
       cats=["skill"], vals=["pct_of_jobs"], order_desc_on="pct_of_jobs"),
    vc("vncmp", 656, 16, 608, 688, "tableEx", "vn_vs_global_compare", "Top ky nang VN vs toan cau",
       table_cols=["rank", "vn_skill", "vn_pct_of_jd", "global_language", "global_worked"]),
]
p4 = [
    vc("em", 16, 16, 624, 688, "clusteredBarChart", "language_signal", "Tang truong nhu cau ngon ngu (%)",
       cats=["language"], vals=["growth_pct"], order_desc_on="growth_pct"),
    vc("dbg", 656, 16, 608, 688, "clusteredBarChart", "database_signal", "Tang truong nhu cau database (%)",
       cats=["database"], vals=["growth_pct"], order_desc_on="growth_pct"),
]
sections = [page("p1", "01 - Tong quan", 0, p1), page("p2", "02 - Cung-cau ky nang", 1, p2),
            page("p3", "03 - Viet Nam (ItViec)", 2, p3), page("p4", "04 - Khuyen nghi", 3, p4)]

# ---------- Ghép Layout (giữ theme/config gốc) ----------
zin = zipfile.ZipFile(SRC)
lay = json.loads(zin.read("Report/Layout").decode("utf-16-le"))
lay["sections"] = sections
new_layout = json.dumps(lay, ensure_ascii=False).encode("utf-16-le")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "Report/Layout":
            data = new_layout
        zout.writestr(item, data)
zin.close()
print("WROTE", OUT)
print("pages:", len(sections), "visuals:", sum(len(s["visualContainers"]) for s in sections))
