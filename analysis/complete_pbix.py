"""
complete_pbix.py — Chèn report 4 trang vào .pbix có sẵn data model.

Tạo visualContainer ĐẦY ĐỦ (config + query + dataTransforms) để Power BI BIND
dữ liệu và HIỂN THỊ — không chỉ tạo khung rỗng. Giữ nguyên DataModel nhị phân.

Dùng: python complete_pbix.py VTI.pbix VTI_completed.pbix
"""
import json, zipfile, uuid, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "VTI.pbix"
OUT = sys.argv[2] if len(sys.argv) > 2 else "VTI_completed.pbix"
NS = uuid.UUID("12345678-1234-5678-1234-567812345678")
def gid(s): return uuid.uuid5(NS, s).hex


def expr_col(entity, prop, src=None):
    ref = {"Source": src} if src else {"Entity": entity}
    return {"Column": {"Expression": {"SourceRef": ref}, "Property": prop}}

def expr_sum(entity, prop, src=None):
    ref = {"Source": src} if src else {"Entity": entity}
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": ref}, "Property": prop}}, "Function": 0}}


def make_vc(vid, x, y, w, h, vtype, entity, title, fields, card_metric=None,
            order_on=None, z=0):
    """
    fields: list of (role, kind, prop). kind='col'|'sum'. role e.g. Category/Y/Values.
    """
    src = "s"
    select, dt_selects = [], []
    proj = {}
    proj_ordering = {}
    for i, (role, kind, prop) in enumerate(fields):
        qn = ("Sum(%s.%s)" % (entity, prop)) if kind == "sum" else ("%s.%s" % (entity, prop))
        if kind == "sum":
            ep = expr_sum(entity, prop, src); ep["Name"] = qn
            ed = expr_sum(entity, prop)
        else:
            ep = expr_col(entity, prop, src); ep["Name"] = qn
            ed = expr_col(entity, prop)
        select.append(ep)
        dt_selects.append({"queryName": qn, "displayName": prop,
                           "roles": {role: True}, "expr": ed})
        proj.setdefault(role, []).append({"queryRef": qn})
        proj_ordering.setdefault(role, []).append(i)

    proto = {"Version": 2, "From": [{"Name": src, "Entity": entity, "Type": 0}],
             "Select": select}
    if order_on:
        proto["OrderBy"] = [{"Direction": 2, "Expression": expr_sum(entity, order_on, src)}]

    binding = {"Primary": {"Groupings": [{"Projections": list(range(len(fields)))}]},
               "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 1000}}},
               "Version": 1}

    config = {
        "name": gid(vid),
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z}}],
        "singleVisual": {
            "visualType": vtype,
            "projections": proj,
            "prototypeQuery": proto,
            "drillFilterOtherVisuals": True,
            "objects": {},
            "vcObjects": {"title": [{"properties": {
                "text": {"expr": {"Literal": {"Value": "'%s'" % title.replace("'", " ")}}},
                "show": {"expr": {"Literal": {"Value": "true"}}}}}]},
        },
    }
    query = {"Commands": [{"SemanticQueryDataShapeCommand": {"Query": proto, "Binding": binding}}]}
    dataTransforms = {"objects": {}, "selects": dt_selects, "projectionOrdering": proj_ordering}

    filters = "[]"
    if card_metric is not None:
        filters = json.dumps([{
            "name": gid(vid + "f"),
            "expression": expr_col(entity, "metric"),
            "filter": {"Version": 2, "From": [{"Name": src, "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {
                           "Expressions": [expr_col(entity, "metric", src)],
                           "Values": [[{"Literal": {"Value": "'%s'" % card_metric}}]]}}}]},
            "type": "Categorical"}])

    return {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z,
            "config": json.dumps(config), "filters": filters,
            "query": json.dumps(query), "dataTransforms": json.dumps(dataTransforms)}


def card(vid, x, y, w, h, title, metric):
    return make_vc(vid, x, y, w, h, "card", "dataset_overview", title,
                   [("Values", "sum", "value")], card_metric=metric)

def bar(vid, x, y, w, h, entity, title, cat, vals, order=None):
    fields = [("Category", "col", cat)] + [("Y", "sum", v) for v in vals]
    return make_vc(vid, x, y, w, h, "clusteredBarChart", entity, title, fields, order_on=order)

def column(vid, x, y, w, h, entity, title, cat, vals, order=None):
    fields = [("Category", "col", cat)] + [("Y", "sum", v) for v in vals]
    return make_vc(vid, x, y, w, h, "clusteredColumnChart", entity, title, fields, order_on=order)

def slicer(vid, x, y, w, h, entity, title, field):
    return make_vc(vid, x, y, w, h, "slicer", entity, title, [("Values", "col", field)])

def table(vid, x, y, w, h, entity, title, cols):
    return make_vc(vid, x, y, w, h, "tableEx", entity, title,
                   [("Values", "col", c) for c in cols])


def page(name, disp, ordinal, vlist):
    return {"id": ordinal, "name": gid(name)[:20], "displayName": disp,
            "filters": "[]", "ordinal": ordinal, "visualContainers": vlist,
            "config": "{}", "displayOption": 1, "width": 1280, "height": 720}


p1 = [
    card("k1", 16, 12, 232, 96, "Developers", "Total respondents"),
    card("k2", 256, 12, 232, 96, "Quoc gia", "Countries covered"),
    card("k3", 496, 12, 232, 96, "Median salary USD", "Median salary USD"),
    card("k4", 736, 12, 250, 96, "Kinh nghiem (nam)", "Median professional coding years"),
    card("k5", 996, 12, 268, 96, "Full-time %", "Employed full-time percentage"),
    bar("lw", 16, 120, 408, 300, "language_signal", "Ngon ngu dang dung", "language", ["worked"], "worked"),
    bar("ld", 432, 120, 408, 300, "language_signal", "Ngon ngu muon dung nam toi", "language", ["desired_next_year"], "desired_next_year"),
    column("ct", 848, 120, 416, 300, "country_distribution", "Top quoc gia (%)", "country", ["pct"], "pct"),
    slicer("s1", 16, 432, 280, 272, "language_signal", "Loc: Tin hieu", "signal"),
    slicer("s2", 312, 432, 280, 272, "role_priority", "Loc: Nhom uu tien", "priority_band"),
    bar("sal", 608, 432, 656, 272, "salary_by_language", "Luong trung vi theo ngon ngu (USD)", "language", ["median_salary"], "median_salary"),
]
p2 = [
    column("db", 16, 16, 624, 340, "database_signal", "Database: dang dung vs muon dung", "database", ["worked", "desired_next_year"], "desired_next_year"),
    bar("gap", 656, 16, 608, 340, "language_signal", "Skill-gap ngon ngu (net change)", "language", ["net_change"], "net_change"),
    bar("ide", 16, 372, 624, 332, "ide_overall", "IDE pho bien (%)", "ide", ["usage_pct"], "usage_pct"),
    bar("role", 656, 372, 608, 332, "role_priority", "Uu tien tuyen dung theo vai tro", "role", ["hiring_priority_score"], "hiring_priority_score"),
]
p3 = [
    bar("vnd", 16, 16, 624, 688, "vn_itviec_skill_demand", "Cau ky nang tai Viet Nam (% tren 1200 JD)", "skill", ["pct_of_jobs"], "pct_of_jobs"),
    table("vncmp", 656, 16, 608, 688, "vn_vs_global_compare", "Top ky nang VN vs toan cau",
          ["rank", "vn_skill", "vn_pct_of_jd", "global_language", "global_worked"]),
]
p4 = [
    bar("em", 16, 16, 624, 688, "language_signal", "Tang truong nhu cau ngon ngu (%)", "language", ["growth_pct"], "growth_pct"),
    bar("dbg", 656, 16, 608, 688, "database_signal", "Tang truong nhu cau database (%)", "database", ["growth_pct"], "growth_pct"),
]
sections = [page("p1", "01 - Tong quan", 0, p1), page("p2", "02 - Cung-cau ky nang", 1, p2),
            page("p3", "03 - Viet Nam (ItViec)", 2, p3), page("p4", "04 - Khuyen nghi", 3, p4)]

zin = zipfile.ZipFile(SRC)
lay = json.loads(zin.read("Report/Layout").decode("utf-16-le"))
lay["sections"] = sections
new_layout = json.dumps(lay, ensure_ascii=False).encode("utf-16-le")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = new_layout if item.filename == "Report/Layout" else zin.read(item.filename)
        zout.writestr(item, data)
zin.close()
print("WROTE", OUT, "| pages:", len(sections), "visuals:", sum(len(s["visualContainers"]) for s in sections))
