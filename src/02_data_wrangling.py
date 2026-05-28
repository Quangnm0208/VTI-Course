"""
===============================================================================
 FINAL PROJECT - VTI ACADEMY
 File:    02_data_wrangling.py
 Mục đích: Làm sạch & GHÉP dữ liệu ItViec (scraping) với khảo sát Stack Overflow
           (Final Project.csv) thành 1 REPORT tổng hợp dạng long-format.

 Đầu vào:
    data/raw/survey_raw.csv      (Final Project.csv đã copy/đổi tên)
    data/raw/itviec_jobs_raw.csv (kết quả scrape ItViec)

 Đầu ra (data/clean/):
    survey_clean.csv          - Khảo sát sau khi clean
    itviec_jobs_clean.csv     - Job ItViec sau khi clean
    skill_report.csv          - REPORT TỔNG HỢP (long-format: skill, source...)
    skill_report.xlsx         - Bản Excel của report (3 sheet)
    skills.db                 - CSDL SQLite chứa các bảng để truy vấn SQL
===============================================================================
"""

# -----------------------------------------------------------------------------
# 1. IMPORT THƯ VIỆN
# -----------------------------------------------------------------------------
import os
import re
import logging
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Optional

# -----------------------------------------------------------------------------
# 2. CẤU HÌNH
# -----------------------------------------------------------------------------
RAW_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)

# Từ điển chuẩn hóa tên kỹ năng (mapping các biến thể về 1 tên duy nhất).
# Dùng cho cả ItViec và Stack Overflow để 2 nguồn có cùng "ngôn ngữ".
SKILL_ALIASES: Dict[str, str] = {
    # JavaScript family
    "js":              "JavaScript",
    "javascript":      "JavaScript",
    "node":            "Node.js",
    "nodejs":          "Node.js",
    "node.js":         "Node.js",
    "reactjs":         "React",
    "react.js":        "React",
    "vuejs":           "Vue.js",
    "vue":             "Vue.js",
    "angularjs":       "Angular",
    "nextjs":          "Next.js",

    # Python
    "python3":         "Python",
    "py":              "Python",

    # .NET / C#
    "c sharp":         "C#",
    "csharp":          "C#",
    ".net":            ".NET",
    "asp.net":         "ASP.NET",
    "dotnet":          ".NET",

    # C/C++
    "cpp":             "C++",
    "c plus plus":     "C++",

    # Databases
    "postgres":        "PostgreSQL",
    "postgresql":      "PostgreSQL",
    "ms sql":          "SQL Server",
    "mssql":           "SQL Server",
    "sqlserver":       "SQL Server",
    "mongo":           "MongoDB",
    "mongodb":         "MongoDB",
    "mysql":           "MySQL",

    # Cloud
    "amazon web services": "AWS",
    "aws":             "AWS",
    "gcp":             "Google Cloud",
    "google cloud platform": "Google Cloud",

    # Mobile
    "react-native":    "React Native",

    # Go
    "golang":          "Go",
}


# -----------------------------------------------------------------------------
# 3. HÀM TIỆN ÍCH
# -----------------------------------------------------------------------------
def to_snake_case(name: str) -> str:
    """
    Đổi tên cột sang snake_case (yêu cầu của đề bài).
    Vd: "Language Worked With" -> "language_worked_with"
    """
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)   # CamelCase -> Camel_Case
    s = re.sub(r"[^A-Za-z0-9]+", "_", s)             # Bỏ ký tự đặc biệt
    return s.strip("_").lower()


def normalize_skill(raw: str) -> str:
    """
    Chuẩn hóa 1 chuỗi kỹ năng: bỏ khoảng trắng, ánh xạ qua SKILL_ALIASES.
    Vd: "  reactjs " -> "React"
    """
    if raw is None:
        return ""
    s = str(raw).strip().lower()
    if not s or s in {"nan", "none", "unknown", "na"}:
        return ""
    # Dùng alias nếu có, không thì viết hoa chữ cái đầu (Title Case)
    return SKILL_ALIASES.get(s, raw.strip())


def report_missing(df: pd.DataFrame, name: str) -> None:
    """In ra số ô NaN nhiều nhất để check chất lượng dữ liệu."""
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(10)
    log.info("[%s] Top cột thiếu dữ liệu:\n%s", name, missing.to_string())


# =============================================================================
# 4. LÀM SẠCH KHẢO SÁT STACK OVERFLOW
# =============================================================================
def clean_survey(df: pd.DataFrame) -> pd.DataFrame:
    """
    Làm sạch khảo sát Stack Overflow (Final Project.csv).

    Các bước:
        B1: Đổi tên cột -> snake_case
        B2: Loại trùng lặp theo respondent_id
        B3: Điền NaN: categorical -> "Unknown"; numeric -> median
        B4: Chuẩn hóa cột số đặc biệt: years_code, years_code_pro, age
            (xử lý "Less than 1 year", "More than 50 years")
        B5: Trim whitespace cho cột text
        B6: Chuẩn hóa cột multi-value (cách nhau bởi ';')
    """
    log.info("=== Wrangling: KHẢO SÁT ===")
    report_missing(df, "Survey RAW")

    # B1. Tên cột
    df = df.rename(columns={c: to_snake_case(c) for c in df.columns})

    # B2. Trùng lặp
    before = len(df)
    if "respondent" in df.columns:
        df = df.drop_duplicates(subset=["respondent"])
    else:
        df = df.drop_duplicates()
    log.info("B2: Loại %d bản ghi trùng lặp", before - len(df))

    # B3. Missing values
    cat_cols = df.select_dtypes(include=["object"]).columns
    df[cat_cols] = df[cat_cols].fillna("Unknown")

    num_cols = df.select_dtypes(include=[np.number]).columns
    for c in num_cols:
        df[c] = df[c].fillna(df[c].median())

    # B4. Cột số đặc biệt
    for col in ["years_code", "years_code_pro"]:
        if col in df.columns:
            df[col] = df[col].replace({
                "Less than 1 year":  "0",
                "More than 50 years": "51",
            })
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df.loc[(df["age"] < 10) | (df["age"] > 99), "age"] = np.nan
        df["age"] = df["age"].fillna(df["age"].median())

    # B5. Trim
    for c in cat_cols:
        df[c] = df[c].astype(str).str.strip()

    # B6. Chuẩn hóa multi-value
    multi_cols = [
        "language_worked_with", "language_desire_next_year",
        "database_worked_with", "database_desire_next_year",
        "platform_worked_with", "platform_desire_next_year",
        "web_frame_worked_with", "web_frame_desire_next_year",
        "misc_tech_worked_with", "misc_tech_desire_next_year",
        "dev_environ",
    ]
    for c in multi_cols:
        if c in df.columns:
            df[c] = (
                df[c].astype(str)
                .str.replace(r"\s*;\s*", ";", regex=True)
                .str.strip()
            )

    log.info("Wrangling khảo sát xong: %d dòng x %d cột", *df.shape)
    return df


# =============================================================================
# 5. LÀM SẠCH ITVIEC JOBS
# =============================================================================
def clean_itviec(df: pd.DataFrame) -> pd.DataFrame:
    """
    Làm sạch dữ liệu tin tuyển dụng ItViec.

    Các bước:
        B1: Tên cột snake_case
        B2: Loại bản ghi rác (thiếu job_title) và trùng lặp
        B3: Chuẩn hóa cột text: trim, lowercase company khi so duplicate
        B4: Chuẩn hóa cột skills: tách ';' -> normalize từng skill -> nối lại
        B5: Chuẩn hóa salary (tách min/max nếu có)
    """
    log.info("=== Wrangling: ITVIEC JOBS ===")
    if df.empty:
        return df

    # B1
    df = df.rename(columns={c: to_snake_case(c) for c in df.columns})

    # B2
    before = len(df)
    df = df.dropna(subset=["job_title"])
    df = df[df["job_title"].astype(str).str.strip() != ""]
    df = df.drop_duplicates(subset=["job_title", "company", "location"])
    log.info("B2: Loại %d bản ghi rác/trùng lặp", before - len(df))

    # B3. Trim text
    for c in ["job_title", "company", "location", "salary"]:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str).str.strip()

    # B4. Chuẩn hóa skills
    def _normalize_skills_field(raw: str) -> str:
        if not raw:
            return ""
        parts = re.split(r"[;,]", str(raw))            # Hỗ trợ cả "," và ";"
        cleaned = {normalize_skill(p) for p in parts}  # Chuẩn hóa từng skill
        cleaned.discard("")
        return ";".join(sorted(cleaned))

    df["skills"] = df.get("skills", "").apply(_normalize_skills_field)

    # B5. Salary: ItViec hay có dạng "1,000 - 2,000 USD" hoặc "Negotiable"
    if "salary" in df.columns:
        df["salary_clean"] = df["salary"].str.replace(",", "", regex=False)
        df["salary_min_usd"] = df["salary_clean"].str.extract(
            r"(\d+)\s*-\s*\d+", expand=False
        )
        df["salary_max_usd"] = df["salary_clean"].str.extract(
            r"\d+\s*-\s*(\d+)", expand=False
        )
        df["salary_min_usd"] = pd.to_numeric(df["salary_min_usd"], errors="coerce")
        df["salary_max_usd"] = pd.to_numeric(df["salary_max_usd"], errors="coerce")
        df = df.drop(columns=["salary_clean"])

    log.info("Wrangling ItViec xong: %d dòng x %d cột", *df.shape)
    return df


# =============================================================================
# 6. CHUYỂN VỀ LONG-FORMAT: 1 DÒNG = 1 KỸ NĂNG (KEY ĐỂ GHÉP)
# =============================================================================
def explode_survey_skills(df: pd.DataFrame) -> pd.DataFrame:
    """
    Từ khảo sát (wide-format), explode các cột multi-value thành long-format:
        columns = [source, country, skill_type, skill_name, respondent_id]
    Đây là bảng FACT chính từ phía Stack Overflow.
    """
    log.info("=== Explode khảo sát thành long-format ===")

    # Map cột -> loại kỹ năng
    col_to_type = {
        "language_worked_with":     "language",
        "database_worked_with":     "database",
        "platform_worked_with":     "platform",
        "web_frame_worked_with":    "web_framework",
        "misc_tech_worked_with":    "misc_tech",
        "dev_environ":              "ide",
    }

    frames = []
    for col, skill_type in col_to_type.items():
        if col not in df.columns:
            continue
        tmp = df[["respondent", "country", col]].copy()
        # Tách string "Python;SQL;Java" -> list -> explode
        tmp[col] = tmp[col].astype(str).str.split(";")
        tmp = tmp.explode(col)
        tmp[col] = tmp[col].apply(normalize_skill)
        tmp = tmp[tmp[col] != ""]                       # Bỏ giá trị rỗng
        tmp = tmp.rename(columns={col: "skill_name", "respondent": "respondent_id"})
        tmp["skill_type"] = skill_type
        tmp["source"] = "StackOverflow"
        frames.append(tmp[["source", "country", "skill_type", "skill_name", "respondent_id"]])

    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    # Bỏ duplicate (cùng người - cùng skill - cùng loại)
    out = out.drop_duplicates()
    log.info("Khảo sát -> %d dòng long-format", len(out))
    return out


def explode_itviec_skills(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode cột skills của ItViec thành long-format:
        columns = [source, country, skill_type, skill_name, job_title, company]
    """
    log.info("=== Explode ItViec thành long-format ===")
    if df.empty or "skills" not in df.columns:
        return pd.DataFrame()

    tmp = df.copy()
    tmp["skills"] = tmp["skills"].astype(str).str.split(";")
    tmp = tmp.explode("skills")
    tmp["skills"] = tmp["skills"].apply(normalize_skill)
    tmp = tmp[tmp["skills"] != ""]

    tmp = tmp.rename(columns={"skills": "skill_name"})
    tmp["source"]     = "ItViec"
    tmp["country"]    = "Vietnam"          # ItViec phục vụ thị trường VN
    tmp["skill_type"] = "job_requirement"  # Đánh dấu nguồn này là yêu cầu JD

    keep = ["source", "country", "skill_type", "skill_name", "job_title", "company"]
    out = tmp[[c for c in keep if c in tmp.columns]].drop_duplicates()
    log.info("ItViec -> %d dòng long-format", len(out))
    return out


# =============================================================================
# 7. GHÉP 2 NGUỒN -> 1 REPORT TỔNG HỢP
# =============================================================================
def build_combined_report(
    df_survey_long: pd.DataFrame,
    df_itviec_long: pd.DataFrame,
) -> pd.DataFrame:
    """
    Ghép 2 nguồn (Stack Overflow + ItViec) thành 1 report tổng hợp.
    Vì 2 nguồn có schema khác nhau, ta dùng pd.concat (union dọc) và
    để pandas tự align cột - cột nào không có sẽ thành NaN.
    """
    log.info("=== Ghép 2 nguồn -> REPORT TỔNG HỢP ===")

    combined = pd.concat([df_survey_long, df_itviec_long], ignore_index=True, sort=False)

    # Sắp xếp lại thứ tự cột cho dễ đọc
    preferred_cols = [
        "source", "country", "skill_type", "skill_name",
        "job_title", "company", "respondent_id",
    ]
    cols = [c for c in preferred_cols if c in combined.columns]
    cols += [c for c in combined.columns if c not in cols]
    combined = combined[cols]

    log.info("Report tổng hợp: %d dòng x %d cột", *combined.shape)
    return combined


def build_skill_summary(combined: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo bảng tổng hợp số lượt xuất hiện của từng kỹ năng từ 2 nguồn.
    Format pivot: skill_name | from_StackOverflow | from_ItViec | total
    Đây là bảng dùng trực tiếp cho Dashboard Power BI.
    """
    log.info("=== Tạo bảng skill summary (pivot) ===")
    if combined.empty:
        return pd.DataFrame()

    # Đếm theo skill_name + source
    pivot = (
        combined.groupby(["skill_name", "source"])
        .size().reset_index(name="count")
        .pivot(index="skill_name", columns="source", values="count")
        .fillna(0).astype(int)
    )
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False).reset_index()
    return pivot


# =============================================================================
# 8. LƯU KẾT QUẢ
# =============================================================================
def save_all(
    df_survey: pd.DataFrame,
    df_itviec: pd.DataFrame,
    df_report: pd.DataFrame,
    df_summary: pd.DataFrame,
) -> None:
    """Xuất tất cả ra CSV, gộp Excel nhiều sheet, và nạp vào SQLite."""
    log.info("=== Lưu file đầu ra ===")

    # ---- CSV ----
    df_survey.to_csv(os.path.join(CLEAN_DIR, "survey_clean.csv"),
                     index=False, encoding="utf-8-sig")
    df_itviec.to_csv(os.path.join(CLEAN_DIR, "itviec_jobs_clean.csv"),
                     index=False, encoding="utf-8-sig")
    df_report.to_csv(os.path.join(CLEAN_DIR, "skill_report.csv"),
                     index=False, encoding="utf-8-sig")
    df_summary.to_csv(os.path.join(CLEAN_DIR, "skill_summary.csv"),
                      index=False, encoding="utf-8-sig")

    # ---- Excel: 1 file - 3 sheet, tiện cho user xem trực tiếp ----
    xlsx_path = os.path.join(CLEAN_DIR, "skill_report.xlsx")
    try:
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            df_report.to_excel(writer,  sheet_name="report",   index=False)
            df_summary.to_excel(writer, sheet_name="summary",  index=False)
            df_itviec.to_excel(writer,  sheet_name="itviec",   index=False)
        log.info("Đã ghi Excel: %s", xlsx_path)
    except ImportError:
        log.warning("Thiếu openpyxl. Chạy: pip install openpyxl")

    # ---- SQLite (cho phần SQL bên dưới) ----
    db_path = os.path.join(CLEAN_DIR, "skills.db")
    conn = sqlite3.connect(db_path)
    try:
        df_survey.to_sql("survey",        conn, if_exists="replace", index=False)
        df_itviec.to_sql("itviec_jobs",   conn, if_exists="replace", index=False)
        df_report.to_sql("skill_report",  conn, if_exists="replace", index=False)
        df_summary.to_sql("skill_summary",conn, if_exists="replace", index=False)
        conn.commit()
        log.info("Đã nạp SQLite: %s", db_path)
    finally:
        conn.close()


# =============================================================================
# 9. HÀM CHÍNH
# =============================================================================
def _read_survey() -> pd.DataFrame:
    """Đọc file khảo sát (.csv hoặc .xlsx) từ data/raw/."""
    for fname in ["survey_raw.csv", "Final Project.csv",
                  "survey_raw.xlsx", "Final Project.xlsx"]:
        path = os.path.join(RAW_DIR, fname)
        if os.path.exists(path):
            log.info("Đọc khảo sát: %s", path)
            if path.endswith(".csv"):
                return pd.read_csv(path, low_memory=False)
            return pd.read_excel(path)
    log.warning("Không có file khảo sát trong %s", RAW_DIR)
    return pd.DataFrame()


def _read_itviec() -> pd.DataFrame:
    path = os.path.join(RAW_DIR, "itviec_jobs_raw.csv")
    if os.path.exists(path):
        log.info("Đọc ItViec: %s", path)
        return pd.read_csv(path)
    log.warning("Không có file ItViec trong %s", RAW_DIR)
    return pd.DataFrame()


def main() -> None:
    log.info("====== BẮT ĐẦU WRANGLING & GHÉP REPORT ======")

    # ---- 1. Đọc dữ liệu raw ----
    df_survey_raw = _read_survey()
    df_itviec_raw = _read_itviec()

    # ---- 2. Clean từng nguồn ----
    df_survey = clean_survey(df_survey_raw)  if not df_survey_raw.empty else df_survey_raw
    df_itviec = clean_itviec(df_itviec_raw)  if not df_itviec_raw.empty else df_itviec_raw

    # ---- 3. Explode về long-format ----
    df_survey_long = explode_survey_skills(df_survey) if not df_survey.empty else pd.DataFrame()
    df_itviec_long = explode_itviec_skills(df_itviec) if not df_itviec.empty else pd.DataFrame()

    # ---- 4. Ghép thành report tổng hợp ----
    df_report = build_combined_report(df_survey_long, df_itviec_long)
    df_summary = build_skill_summary(df_report)

    # ---- 5. Lưu kết quả ----
    save_all(df_survey, df_itviec, df_report, df_summary)

    log.info("====== HOÀN TẤT - Xem file tại data/clean/ ======")


if __name__ == "__main__":
    main()
