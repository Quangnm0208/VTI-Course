"""
vti_hr_curriculum_market_insight.py
===================================================================
Module phân tích dùng chung cho notebook `vti_hr_curriculum_market_insight.ipynb`
và khi chạy dòng lệnh. Tất cả số liệu trong notebook đều gọi các hàm ở đây để
notebook và CLI luôn khớp nhau.

Đầu vào: Final Project.csv (khảo sát Stack Overflow, ~11.552 dòng).
Cách dùng nhanh:
    from vti_hr_curriculum_market_insight import load_data, prepare_data, ...
    df = prepare_data(load_data('Final Project.csv'))

Ghi chú: các hàm thống kê (overview, market_signal, salary_by_language,
role_ide_matrix, dataset_profile, build_clean_dataset) tái lập CHÍNH XÁC kết quả
trong notebook. Các bảng chiến lược HR (hành động, JD, rubric, roadmap) trả về
nội dung đã chốt — đồng bộ với analysis/market_insight_data.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

# ----- Tham số phân tích -----
SALARY_CAP = 300_000          # winsorize trần lương (USD) để cắt ngoại lai tự khai
MIN_SALARY_SAMPLE = 100       # cỡ mẫu tối thiểu khi tính lương theo ngôn ngữ
EMERGING_PCT = 20             # |growth_pct| >= 20 -> Emerging/Declining, còn lại Stable

# Map cột multi-select -> nhãn
_LANG_SEP = ";"

# Map DevType (substring) -> vai trò chuẩn hóa cho phân tích HR.
_ROLE_RULES = [
    ("Data scientist", "Data Scientist / ML"),
    ("machine learning", "Data Scientist / ML"),
    ("Data or business analyst", "Data/BI Analyst"),
    ("DevOps", "DevOps Specialist"),
    ("Full-stack", "Full-stack Developer"),
    ("Back-end", "Back-end Developer"),
    ("Front-end", "Front-end Developer"),
    ("Mobile", "Mobile Developer"),
    ("Product manager", "Product/BA"),
    ("Engineering manager", "Product/BA"),
]


# =============================================================================
# 1. ĐỌC & CHUẨN BỊ
# =============================================================================
def load_data(path: str | Path) -> pd.DataFrame:
    """Đọc Final Project.csv. Giữ nguyên tên cột gốc (CamelCase)."""
    return pd.read_csv(path, low_memory=False)


def _years_to_num(val) -> float:
    s = str(val).strip()
    if s in {"Less than 1 year"}:
        return 0.5
    if s in {"More than 50 years"}:
        return 51.0
    try:
        return float(s)
    except ValueError:
        return np.nan


def _count_multi(series: pd.Series) -> pd.Series:
    return (series.fillna("").astype(str)
            .apply(lambda s: len([x for x in s.split(_LANG_SEP) if x.strip()])))


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm các cột phái sinh (giữ cột gốc để market_signal dùng tên CamelCase):
        salary_usd, salary_winsorized, years_code_pro_num,
        language_count_worked, language_count_desired
    """
    df = raw.copy()
    if "ConvertedComp" in df.columns:
        df["salary_usd"] = pd.to_numeric(df["ConvertedComp"], errors="coerce")
        df["salary_winsorized"] = df["salary_usd"].clip(upper=SALARY_CAP)
    if "YearsCodePro" in df.columns:
        df["years_code_pro_num"] = df["YearsCodePro"].apply(_years_to_num)
    if "LanguageWorkedWith" in df.columns:
        df["language_count_worked"] = _count_multi(df["LanguageWorkedWith"])
    if "LanguageDesireNextYear" in df.columns:
        df["language_count_desired"] = _count_multi(df["LanguageDesireNextYear"])
    return df


# =============================================================================
# 2. TỔNG QUAN & TỪ ĐIỂN & CHẤT LƯỢNG
# =============================================================================
def dataset_overview(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    vn = df["Country"].isin(["Viet Nam", "Vietnam"]).sum() if "Country" in df else 0
    ft = (df["Employment"] == "Employed full-time").mean() * 100 if "Employment" in df else np.nan
    med_sal = df["salary_winsorized"].median() if "salary_winsorized" in df else np.nan
    med_yr = df["years_code_pro_num"].median() if "years_code_pro_num" in df else np.nan
    avg_w = df["language_count_worked"].mean() if "language_count_worked" in df else np.nan
    avg_d = df["language_count_desired"].mean() if "language_count_desired" in df else np.nan
    rows = [
        ("Total respondents", float(n), "Large enough for global talent signal and curriculum."),
        ("Countries covered", float(df["Country"].nunique()) if "Country" in df else np.nan,
         "Useful for global benchmark, not only one location."),
        ("Viet Nam responses", float(vn), "Vietnam sample is small; HR should validate locally."),
        ("Median salary USD", round(float(med_sal)) if pd.notna(med_sal) else np.nan,
         "Use median as reference point for compensation."),
        ("Median professional coding years", round(float(med_yr)) if pd.notna(med_yr) else np.nan,
         "The survey reflects mid-level professional developers."),
        ("Employed full-time percentage", round(float(ft), 1) if pd.notna(ft) else np.nan,
         "Signals are relevant for professional hiring."),
        ("Average languages worked per respondent", round(float(avg_w), 1) if pd.notna(avg_w) else np.nan,
         "Modern developers are polyglot; JD and training should reflect this."),
        ("Average languages desired per respondent", round(float(avg_d), 1) if pd.notna(avg_d) else np.nan,
         "Candidates want multi-skill growth; learning paths matter."),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "hr_meaning"])


def data_dictionary_table() -> pd.DataFrame:
    rows = [
        ("Respondent", "Mã ID người trả lời được ngẫu nhiên hóa.", "Khóa định danh để đếm số developer."),
        ("Country", "Bạn hiện đang cư trú ở quốc gia nào?", "Tách tín hiệu toàn cầu với Việt Nam."),
        ("Employment", "Tình trạng việc làm hiện tại của bạn?", "Đo tỷ lệ làm toàn thời gian."),
        ("DevType", "Những điều nào sau đây mô tả về bạn? (chọn nhiều)", "Nhận diện vai trò để xếp ưu tiên tuyển dụng."),
        ("YearsCodePro", "Bạn đã viết mã chuyên nghiệp được bao nhiêu năm?", "Quy đổi về số năm kinh nghiệm."),
        ("ConvertedComp", "Tổng thu nhập quy đổi sang USD mỗi năm.", "Tín hiệu lương; winsorize rồi lấy trung vị."),
        ("LanguageWorkedWith", "Ngôn ngữ đã làm việc trong năm qua (chọn nhiều).", "Vế 'đang dùng' của tín hiệu ngôn ngữ."),
        ("LanguageDesireNextYear", "Ngôn ngữ muốn làm việc năm tới (chọn nhiều).", "Vế 'muốn dùng' để tính tăng trưởng."),
        ("DatabaseWorkedWith", "Cơ sở dữ liệu đã làm việc trong năm qua.", "Vế 'đang dùng' của tín hiệu CSDL."),
        ("DatabaseDesireNextYear", "Cơ sở dữ liệu muốn làm việc năm tới.", "Vế 'muốn dùng' để chọn CSDL trục chính."),
        ("DevEnviron", "Môi trường phát triển (IDE) thường dùng.", "Phân tích IDE theo vai trò để chọn công cụ onboarding."),
    ]
    return pd.DataFrame(rows, columns=["column_name", "survey_question_vi", "role_in_analysis"])


_PROFILE_COLS = [
    "DatabaseDesireNextYear", "ConvertedComp", "DatabaseWorkedWith",
    "LanguageDesireNextYear", "DevType", "DevEnviron", "LanguageWorkedWith",
    "YearsCodePro", "Employment", "Respondent", "Country",
]


def dataset_profile(df: pd.DataFrame) -> dict:
    n = len(df)
    miss_rows = []
    for c in _PROFILE_COLS:
        if c in df.columns:
            cnt = int(df[c].isna().sum())
            miss_rows.append((c, cnt, round(cnt / n * 100, 1)))
    missing = (pd.DataFrame(miss_rows, columns=["column_name", "missing_count", "missing_pct"])
               .sort_values("missing_pct", ascending=False).reset_index(drop=True))
    ctry = (df["Country"].value_counts().head(8).reset_index())
    ctry.columns = ["Country", "count"]
    ctry["pct"] = (ctry["count"] / n * 100).round(1)
    return {"missing": missing, "country": ctry}


def build_clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Đổi mọi tên cột về snake_case (đáp ứng sản phẩm nộp clean dataset)."""
    def snake(name):
        s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name))
        s = re.sub(r"[^0-9a-zA-Z]+", "_", s)
        return s.strip("_").lower()
    return df.rename(columns={c: snake(c) for c in df.columns})


# =============================================================================
# 3. TÍN HIỆU THỊ TRƯỜNG (ngôn ngữ / CSDL)
# =============================================================================
def _explode_count(df: pd.DataFrame, col: str) -> pd.Series:
    """Đếm số respondent (unique) cho mỗi skill trong 1 cột multi-select."""
    if col not in df.columns:
        return pd.Series(dtype=int)
    s = (df[col].dropna().astype(str).str.split(_LANG_SEP).explode()
         .str.strip())
    s = s[s != ""]
    return s.value_counts()


def market_signal(df: pd.DataFrame, worked_col: str, desired_col: str,
                  label: str = "skill") -> pd.DataFrame:
    """
    Tín hiệu thị trường cho 1 nhóm skill:
        worked, desired_next_year, net_change, growth_pct, desired_market_pct, signal
    signal = Emerging/Declining/Stable theo ngưỡng |growth_pct| >= EMERGING_PCT.
    Sắp xếp theo desired_next_year giảm dần (như notebook).
    """
    n = len(df)
    w = _explode_count(df, worked_col)
    d = _explode_count(df, desired_col)
    skills = sorted(set(w.index) | set(d.index))
    rows = []
    for sk in skills:
        worked = int(w.get(sk, 0))
        desired = int(d.get(sk, 0))
        net = desired - worked
        gpct = round(net / worked * 100, 1) if worked else np.nan
        dmp = round(desired / n * 100, 1)
        if pd.isna(gpct):
            sig = "Emerging"
        elif gpct >= EMERGING_PCT:
            sig = "Emerging"
        elif gpct <= -EMERGING_PCT:
            sig = "Declining"
        else:
            sig = "Stable"
        rows.append((sk, worked, desired, net, gpct, dmp, sig))
    out = pd.DataFrame(rows, columns=[label, "worked", "desired_next_year",
                                      "net_change", "growth_pct",
                                      "desired_market_pct", "signal"])
    return out.sort_values("desired_next_year", ascending=False).reset_index(drop=True)


# =============================================================================
# 4. IDE THEO VAI TRÒ
# =============================================================================
def _role_of(devtype: str) -> str | None:
    if not isinstance(devtype, str):
        return None
    for key, role in _ROLE_RULES:
        if key.lower() in devtype.lower():
            return role
    return None


def _explode_roles(df: pd.DataFrame) -> pd.DataFrame:
    """Mỗi respondent có thể nhiều DevType -> nhiều role. Trả long-format."""
    tmp = df[["DevType"]].copy()
    tmp["_idx"] = np.arange(len(tmp))
    tmp["role"] = tmp["DevType"].astype(str).str.split(_LANG_SEP)
    tmp = tmp.explode("role")
    tmp["role"] = tmp["role"].apply(_role_of)
    tmp = tmp.dropna(subset=["role"])
    return tmp[["_idx", "role"]]


def role_ide_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Số developer theo (vai trò, IDE), kèm rank trong mỗi vai trò."""
    roles = _explode_roles(df)
    ide = df[["DevEnviron"]].copy()
    ide["_idx"] = np.arange(len(ide))
    ide["ide"] = ide["DevEnviron"].astype(str).str.split(_LANG_SEP)
    ide = ide.explode("ide")
    ide["ide"] = ide["ide"].str.strip()
    ide = ide[ide["ide"] != ""]
    merged = roles.merge(ide[["_idx", "ide"]], on="_idx", how="inner")
    g = (merged.groupby(["role", "ide"])["_idx"].nunique()
         .reset_index(name="developer_count"))
    g["rank"] = g.groupby("role")["developer_count"].rank(method="first", ascending=False).astype(int)
    return g.sort_values(["role", "rank"]).reset_index(drop=True)


# =============================================================================
# 5. LƯƠNG THEO NGÔN NGỮ
# =============================================================================
def salary_by_language(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lương trung vị/trung bình theo ngôn ngữ (dùng salary_winsorized), chỉ giữ
    ngôn ngữ có >= MIN_SALARY_SAMPLE người có lương. Sort theo median giảm dần.
    """
    sal_col = "salary_winsorized" if "salary_winsorized" in df.columns else "salary_usd"
    base = df[df[sal_col].notna()].copy()
    global_mean = base[sal_col].mean()
    rows = []
    langs = (base["LanguageWorkedWith"].dropna().astype(str)
             .str.split(_LANG_SEP).explode().str.strip())
    langs = langs[langs != ""].unique()
    for lg in langs:
        mask = base["LanguageWorkedWith"].astype(str).str.contains(
            rf"(?:^|;)\s*{re.escape(lg)}\s*(?:;|$)", regex=True)
        sub = base.loc[mask, sal_col]
        if len(sub) >= MIN_SALARY_SAMPLE:
            rows.append((lg, len(sub), round(sub.median()), round(sub.mean()),
                         round((sub.mean() / global_mean - 1) * 100, 1)))
    out = pd.DataFrame(rows, columns=["language", "developer_count", "median_salary",
                                      "mean_salary", "mean_vs_global_pct"])
    return out.sort_values("median_salary", ascending=False).reset_index(drop=True)


def salary_growth_cross_insight(language_signal: pd.DataFrame,
                                salary_language: pd.DataFrame) -> pd.DataFrame:
    """Ghép tín hiệu tăng trưởng với lương để tìm 'skill vàng'."""
    merged = language_signal.merge(
        salary_language[["language", "developer_count", "median_salary", "mean_salary"]]
        .rename(columns={"developer_count": "salary_sample_size"}),
        on="language", how="left")

    def rec(r):
        if r["signal"] == "Emerging" and (r["desired_next_year"] >= 3000):
            return "Mass-market growth skill"
        if r["signal"] == "Declining" and r["desired_next_year"] >= 3000:
            return "Keep as foundation, but avoid over-expansion"
        return "Monitor"
    merged["recommendation"] = merged.apply(rec, axis=1)
    return merged


# =============================================================================
# 6. VAI TRÒ & ƯU TIÊN TUYỂN DỤNG
# =============================================================================
def role_summary_for_hr(df: pd.DataFrame) -> pd.DataFrame:
    roles = _explode_roles(df)
    sal_col = "salary_winsorized" if "salary_winsorized" in df.columns else "salary_usd"
    sal = df[[sal_col]].copy()
    sal["_idx"] = np.arange(len(sal))
    merged = roles.merge(sal, on="_idx", how="left")
    g = merged.groupby("role").agg(
        developer_count=("_idx", "nunique"),
        median_salary=(sal_col, "median")).reset_index()
    g["median_salary"] = g["median_salary"].round()
    return g.sort_values("developer_count", ascending=False).reset_index(drop=True)


def role_skill_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Top ngôn ngữ phổ biến cho mỗi vai trò (long-format role x language)."""
    roles = _explode_roles(df)
    lang = df[["LanguageWorkedWith"]].copy()
    lang["_idx"] = np.arange(len(lang))
    lang["language"] = lang["LanguageWorkedWith"].astype(str).str.split(_LANG_SEP)
    lang = lang.explode("language")
    lang["language"] = lang["language"].str.strip()
    lang = lang[lang["language"] != ""]
    merged = roles.merge(lang[["_idx", "language"]], on="_idx", how="inner")
    g = (merged.groupby(["role", "language"])["_idx"].nunique()
         .reset_index(name="developer_count"))
    g["rank"] = g.groupby("role")["developer_count"].rank(method="first", ascending=False).astype(int)
    return g.sort_values(["role", "rank"]).reset_index(drop=True)


def hr_role_priority(role_summary: pd.DataFrame, role_skills: pd.DataFrame) -> pd.DataFrame:
    """
    Điểm ưu tiên = chuẩn hóa min-max của demand (số dev) [trọng số 0.7] +
    salary [0.3], quy về thang 100. Band: >=60 P1, 40-60 P2, <40 P3.
    (Công thức minh bạch; notebook hiển thị kết quả tương ứng.)
    """
    r = role_summary.copy()
    def norm(s):
        rng = s.max() - s.min()
        return (s - s.min()) / rng if rng else s * 0
    r["score"] = (0.7 * norm(r["developer_count"]) + 0.3 * norm(r["median_salary"]))
    r["hiring_priority_score"] = (r["score"] * 100).round(1)
    r["priority_band"] = np.select(
        [r["hiring_priority_score"] >= 60, r["hiring_priority_score"] >= 40],
        ["Priority 1", "Priority 2"], default="Priority 3")
    return (r.drop(columns=["score"])
            .sort_values("hiring_priority_score", ascending=False).reset_index(drop=True))


# =============================================================================
# 7. CÁC BẢNG CHIẾN LƯỢC HR (đồng bộ với market_insight_data.py)
# =============================================================================
def hr_action_plan(overview=None, language_signal=None, database_signal=None,
                   role_priority=None) -> pd.DataFrame:
    rows = [
        ("Workforce planning",
         "Translate skill demand into a yearly headcount and training plan.",
         "11,552 respondents; top desired languages: JavaScript, Python, SQL, TypeScript.",
         "Prioritize role tracks: Full-stack, Back-end, DevOps, Front-end.",
         "Global survey may not fully represent Vietnam demand."),
        ("Recruitment sourcing",
         "Use emerging skills as sourcing tags, not only screening filters.",
         "Emerging language signals: TypeScript, Go, Kotlin, Rust.",
         "Create Boolean keyword strings for LinkedIn, TopCV, ItViec.",
         "Overusing niche tags can shrink candidate pool."),
        ("Job description design",
         "Separate must-have skills from nice-to-have growth skills.",
         "Top database signals: PostgreSQL, MongoDB, Redis, Elasticsearch.",
         "Write JDs in 3 layers: foundation, role-specific, growth.",
         "Too many keywords make JD unrealistic and reduce applies."),
        ("Interview design",
         "Turn skill signals into a structured interview rubric.",
         "The market is multi-stack; average developer uses ~5 languages.",
         "Use a 100-point rubric: technical core, database, tooling, project.",
         "Unstructured interviews over-weight confidence over evidence."),
        ("Compensation benchmarking",
         "Use median salary and sample size together before setting bands.",
         "Salary is self-reported with outliers; median is winsorized at $300k.",
         "Create compensation bands by role, validate with Vietnam data.",
         "Vietnam responses are only 12; do not localize blindly."),
        ("Learning and development",
         "Use the same insight to reskill internal trainers and curriculum.",
         "VS Code dominates; PostgreSQL/NoSQL rising; Cloud/DevOps pays most.",
         "Build a 4-week enablement path: VS Code/Git, SQL, role stack, project.",
         "Training without project assessment may look good but lack proof."),
    ]
    return pd.DataFrame(rows, columns=[
        "hr_area", "what_hr_can_do", "evidence_from_data",
        "immediate_action", "risk"])


def jd_keyword_map(role_priority=None) -> pd.DataFrame:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import market_insight_data as M
    j = M.jd_keyword_map().copy()
    j["jd_rule"] = ("Keep must-have list short. Use growth keywords as "
                    "preferred-but-not-required to widen the funnel.")
    return j


def interview_rubric() -> pd.DataFrame:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import market_insight_data as M
    return M.interview_rubric()


def training_roadmap() -> pd.DataFrame:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import market_insight_data as M
    return M.training_roadmap()


def make_executive_summary(overview, language_signal=None, database_signal=None,
                           role_priority=None, salary_language=None,
                           hr_plan=None) -> str:
    ov = overview.set_index("metric")["value"]
    n = int(ov.get("Total respondents", 0))
    nc = int(ov.get("Countries covered", 0))
    sal = int(ov.get("Median salary USD", 0))
    vn = int(ov.get("Viet Nam responses", 0))
    return (
        "VTI Academy - HR and Curriculum Market Insight\n\n"
        "Executive reading\n"
        f"The dataset contains {n:,} developers across {nc} countries. "
        f"Median salary is ${sal:,}/year.\n"
        f"Vietnam has {vn} responses, so this file is strong for global trend "
        "reading but weak for Vietnam-only salary or supply conclusions.\n\n"
        "What HR can do with this insight\n"
        "1. Workforce planning: prioritize role tracks where demand, salary and "
        "growth skills overlap.\n"
        "2. Recruitment sourcing: use emerging skills (TypeScript, Go, Kotlin, "
        "Rust) as sourcing tags, keep foundation skills in screening.\n"
        "3. JD design: split skills into must-have, role-specific and nice-to-have "
        "growth.\n"
        "4. L&D: standardize on VS Code + Git + PostgreSQL, then add a role stack.\n"
        "Final principle: do not hire or open a course for a single hot technology; "
        "prioritize the overlap of demand, growth, salary and role fit."
    )


# =============================================================================
# CLI tiện kiểm tra nhanh
# =============================================================================
if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "Final Project.csv"
    if not Path(path).exists():
        print(f"[!] Không thấy {path}. Hãy đặt Final Project.csv cạnh file này.")
        raise SystemExit(1)
    df = prepare_data(load_data(path))
    print(dataset_overview(df).to_string(index=False))
    print()
    print(market_signal(df, "LanguageWorkedWith", "LanguageDesireNextYear", "language").head(10).to_string(index=False))
