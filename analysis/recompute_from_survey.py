"""
recompute_from_survey.py — Tính lại các bảng phân tích từ khảo sát Stack Overflow
bản mới (results.txt) theo ĐÚNG logic cũ, chỉ thay tên cột cho phù hợp survey 2025.

Logic giữ nguyên:
  - market_signal: đếm respondent unique cho mỗi skill ở cột "đang dùng" và
    "muốn dùng", net_change = desired - worked, growth_pct, signal theo ngưỡng ±20%.
  - salary_by_language: winsorize lương ở $300k, trung vị theo ngôn ngữ, cỡ mẫu >=100.
  - role_priority: map DevType -> vai trò, điểm = 0.7*demand + 0.3*salary (chuẩn hóa).

Ánh xạ cột (2019 -> 2025):
  Respondent->ResponseId, LanguageWorkedWith->LanguageHaveWorkedWith,
  LanguageDesireNextYear->LanguageWantToWorkWith, DatabaseWorkedWith->DatabaseHaveWorkedWith,
  DatabaseDesireNextYear->DatabaseWantToWorkWith, ConvertedComp->ConvertedCompYearly,
  YearsCodePro->WorkExp. (Survey 2025 BỎ câu hỏi IDE -> giữ bảng IDE kỳ trước.)

Đầu ra: analysis/market_data.json (các bảng số liệu mới) để market_insight_data.py nạp.

Chạy: python analysis/recompute_from_survey.py "data/raw/results.txt"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "market_data.json"

SALARY_CAP = 300_000
MIN_SALARY_SAMPLE = 100
EMERGING_PCT = 20
SEP = ";"

COLS = {
    "id": "ResponseId", "country": "Country", "employment": "Employment",
    "devtype": "DevType", "exp": "WorkExp", "salary": "ConvertedCompYearly",
    "lang_w": "LanguageHaveWorkedWith", "lang_d": "LanguageWantToWorkWith",
    "db_w": "DatabaseHaveWorkedWith", "db_d": "DatabaseWantToWorkWith",
}

_ROLE_RULES = [
    ("Data scientist", "Data Scientist / ML"), ("machine learning", "Data Scientist / ML"),
    ("Data or business analyst", "Data/BI Analyst"), ("DevOps", "DevOps Specialist"),
    ("Full-stack", "Full-stack Developer"), ("Back-end", "Back-end Developer"),
    ("Front-end", "Front-end Developer"), ("Mobile", "Mobile Developer"),
    ("Product manager", "Product/BA"), ("Engineering manager", "Product/BA"),
]


def explode_count(s: pd.Series) -> pd.Series:
    x = s.dropna().astype(str).str.split(SEP).explode().str.strip()
    return x[x != ""].value_counts()


def market_signal(df, wcol, dcol, label):
    n = len(df)
    w, d = explode_count(df[wcol]), explode_count(df[dcol])
    rows = []
    for sk in sorted(set(w.index) | set(d.index)):
        worked, desired = int(w.get(sk, 0)), int(d.get(sk, 0))
        net = desired - worked
        g = round(net / worked * 100, 1) if worked else np.nan
        sig = ("Emerging" if (pd.isna(g) or g >= EMERGING_PCT)
               else "Declining" if g <= -EMERGING_PCT else "Stable")
        rows.append((sk, worked, desired, net, g, round(desired / n * 100, 1), sig))
    out = pd.DataFrame(rows, columns=[label, "worked", "desired_next_year",
                                      "net_change", "growth_pct", "desired_market_pct", "signal"])
    # bỏ "NA"/rỗng nếu lọt
    out = out[~out[label].str.lower().isin(["nan", "na", ""])]
    return out.sort_values("desired_next_year", ascending=False).reset_index(drop=True)


def salary_by_language(df):
    s = pd.to_numeric(df[COLS["salary"]], errors="coerce").clip(upper=SALARY_CAP)
    base = df.assign(_sal=s).dropna(subset=["_sal"])
    gmean = base["_sal"].mean()
    langs = explode_count(base[COLS["lang_w"]]).index
    rows = []
    for lg in langs:
        mask = base[COLS["lang_w"]].astype(str).str.contains(
            rf"(?:^|;)\s*{__import__('re').escape(lg)}\s*(?:;|$)", regex=True)
        sub = base.loc[mask, "_sal"]
        if len(sub) >= MIN_SALARY_SAMPLE:
            rows.append((lg, int(len(sub)), round(sub.median()), round(sub.mean()),
                         round((sub.mean() / gmean - 1) * 100, 1)))
    out = pd.DataFrame(rows, columns=["language", "developer_count", "median_salary",
                                      "mean_salary", "mean_vs_global_pct"])
    return out.sort_values("median_salary", ascending=False).reset_index(drop=True)


def role_of(dt):
    if not isinstance(dt, str):
        return None
    for k, r in _ROLE_RULES:
        if k.lower() in dt.lower():
            return r
    return None


def role_priority(df):
    s = pd.to_numeric(df[COLS["salary"]], errors="coerce").clip(upper=SALARY_CAP)
    tmp = df.assign(_sal=s)
    tmp = tmp.assign(role=tmp[COLS["devtype"]].astype(str).str.split(SEP)).explode("role")
    tmp["role"] = tmp["role"].str.strip().map(role_of)
    tmp = tmp.dropna(subset=["role"])
    g = tmp.groupby("role").agg(developer_count=(COLS["id"], "nunique"),
                                median_salary=("_sal", "median")).reset_index()
    g["median_salary"] = g["median_salary"].round()

    def norm(c):
        rng = c.max() - c.min()
        return (c - c.min()) / rng if rng else c * 0
    g["score"] = 0.7 * norm(g["developer_count"]) + 0.3 * norm(g["median_salary"])
    g["hiring_priority_score"] = (g["score"] * 100).round(1)
    g["priority_band"] = np.select(
        [g["hiring_priority_score"] >= 60, g["hiring_priority_score"] >= 40],
        ["Priority 1", "Priority 2"], default="Priority 3")
    return (g.drop(columns="score").sort_values("hiring_priority_score", ascending=False)
            .reset_index(drop=True))


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "raw" / "results.txt"
    use = list(COLS.values())
    df = pd.read_csv(path, usecols=lambda c: c in use, low_memory=False)
    n = len(df)
    print(f"Đọc {n:,} dòng từ {path.name}")

    exp = pd.to_numeric(df[COLS["exp"]], errors="coerce")
    sal = pd.to_numeric(df[COLS["salary"]], errors="coerce").clip(upper=SALARY_CAP)
    vn = int(df[COLS["country"]].astype(str).str.contains("Viet Nam|Vietnam", case=False, na=False).sum())
    # SO 2025 gộp việc làm thành "Employed" (không tách full-time). Dùng tỷ lệ
    # respondent có việc làm chính thức ("Employed") làm tín hiệu mẫu chuyên nghiệp.
    ft = round((df[COLS["employment"]].astype(str).str.strip() == "Employed").mean() * 100, 1)
    lw = df[COLS["lang_w"]].fillna("").astype(str).apply(lambda s: len([x for x in s.split(SEP) if x.strip()]))
    ld = df[COLS["lang_d"]].fillna("").astype(str).apply(lambda s: len([x for x in s.split(SEP) if x.strip()]))

    overview = [
        ["Total respondents", float(n)],
        ["Countries covered", float(df[COLS["country"]].nunique())],
        ["Viet Nam responses", float(vn)],
        ["Median salary USD", round(float(sal.median()))],
        ["Median professional coding years", round(float(exp.median())) if exp.notna().any() else 0],
        ["Employed full-time percentage", ft],
        ["Average languages worked per respondent", round(float(lw.mean()), 1)],
        ["Average languages desired per respondent", round(float(ld.mean()), 1)],
    ]
    short = {
        "United States of America": "United States",
        "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
        "Russian Federation": "Russia", "Iran, Islamic Republic of...": "Iran",
    }
    ctry = (df[COLS["country"]].value_counts().head(8).reset_index())
    ctry.columns = ["country", "count"]
    ctry["country"] = ctry["country"].replace(short)
    ctry["pct"] = (ctry["count"] / n * 100).round(1)

    data = {
        "_meta": {"source": "Stack Overflow Developer Survey 2025", "respondents": n,
                  "file": path.name},
        "dataset_overview": overview,
        "language_signal": market_signal(df, COLS["lang_w"], COLS["lang_d"], "language").to_dict("records"),
        "database_signal": market_signal(df, COLS["db_w"], COLS["db_d"], "database").to_dict("records"),
        "salary_by_language": salary_by_language(df).to_dict("records"),
        "role_priority": role_priority(df).to_dict("records"),
        "country_distribution": ctry.to_dict("records"),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[ok] -> {OUT.relative_to(ROOT)}")
    print("Top languages (worked):",
          [r["language"] for r in sorted(data["language_signal"], key=lambda x: -x["worked"])[:6]])
    print("Median salary USD:", overview[3][1], "| countries:", overview[1][1], "| VN:", vn)


if __name__ == "__main__":
    main()
