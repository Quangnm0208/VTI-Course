"""
utils.py — Hàm tái sử dụng cho pipeline phân tích kỹ năng IT (VTI Academy).

Toàn bộ hàm theo đúng yêu cầu đề bài:
    load_data, standardize_column_names, clean_numeric_columns,
    split_multiselect_column, calculate_frequency_table, calculate_skill_gap,
    export_clean_data, export_summary_tables

Nguyên tắc:
    - Không hard-code đường dẫn tuyệt đối (nhận path qua tham số).
    - Kiểm tra file tồn tại, xử lý thiếu dữ liệu, không bịa số.
    - Mỗi bước có input/output rõ ràng + comment.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# Ánh xạ tên cột khảo sát -> snake_case "đẹp" cho các cột hay dùng. Các cột
# khác sẽ được snake_case tự động.
COLUMN_RENAME = {
    "Respondent": "respondent_id",
    "ConvertedComp": "comp_total",
    "LanguageWorkedWith": "language_worked_with",
    "LanguageDesireNextYear": "language_desire_next_year",
    "DatabaseWorkedWith": "database_worked_with",
    "DatabaseDesireNextYear": "database_desire_next_year",
    "PlatformWorkedWith": "platform_worked_with",
    "PlatformDesireNextYear": "platform_desire_next_year",
    "WebFrameWorkedWith": "webframe_worked_with",
    "WebFrameDesireNextYear": "webframe_desire_next_year",
    "MiscTechWorkedWith": "misc_tech_worked_with",
    "MiscTechDesireNextYear": "misc_tech_desire_next_year",
    "DevEnviron": "dev_environment",
    "OpSys": "operating_system",
    "DevType": "dev_type",
    "YearsCode": "years_code",
    "YearsCodePro": "years_code_pro",
    "WorkWeekHrs": "work_week_hrs",
}

# Cột multi-select (giá trị phân tách bởi ';') -> nhóm danh mục skill.
MULTISELECT_CATEGORY = {
    "language_worked_with": "programming_language",
    "language_desire_next_year": "programming_language",
    "database_worked_with": "database",
    "database_desire_next_year": "database",
    "platform_worked_with": "platform",
    "platform_desire_next_year": "platform",
    "webframe_worked_with": "web_framework",
    "webframe_desire_next_year": "web_framework",
    "misc_tech_worked_with": "misc_tech",
    "misc_tech_desire_next_year": "misc_tech",
    "dev_environment": "ide",
}

# Chuẩn hóa biến thể tên skill về một dạng duy nhất.
SKILL_ALIASES = {
    "js": "JavaScript", "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js",
    "reactjs": "React", "react.js": "React", "vuejs": "Vue.js", "vue": "Vue.js",
    "python3": "Python", "py": "Python", "c sharp": "C#", "csharp": "C#",
    "postgres": "PostgreSQL", "ms sql": "Microsoft SQL Server",
    "mssql": "Microsoft SQL Server", "sqlserver": "Microsoft SQL Server",
    "mongo": "MongoDB", "golang": "Go", "vs code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
}


# -----------------------------------------------------------------------------
# 1. ĐỌC DỮ LIỆU
# -----------------------------------------------------------------------------
def load_data(path: str | Path) -> pd.DataFrame:
    """
    Đọc dataset (.csv hoặc .xlsx). Kiểm tra file tồn tại trước khi đọc.
    Có log nguồn + số bản ghi (yêu cầu đề bài: ghi rõ nguồn/ngày/số dòng).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file dữ liệu: {p}. "
            f"Hãy đặt 'Final Project.csv' vào data/raw/ rồi chạy lại."
        )
    if p.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p, low_memory=False)
    log.info("Đã đọc %s -> %d dòng x %d cột", p.name, len(df), df.shape[1])
    return df


# -----------------------------------------------------------------------------
# 2. CHUẨN HÓA TÊN CỘT
# -----------------------------------------------------------------------------
def _snake(name: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name))
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s)
    return s.strip("_").lower()


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Đổi tên cột -> snake_case rõ ràng, không dấu cách/ký tự đặc biệt."""
    rename = {}
    for c in df.columns:
        rename[c] = COLUMN_RENAME.get(c, _snake(c))
    out = df.rename(columns=rename)
    log.info("Chuẩn hóa %d tên cột về snake_case", len(rename))
    return out


# -----------------------------------------------------------------------------
# 3. CHUẨN HÓA CỘT SỐ
# -----------------------------------------------------------------------------
def clean_numeric_columns(df: pd.DataFrame,
                          columns: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """
    Ép cột số về numeric, xử lý các nhãn đặc biệt của khảo sát:
        'Less than 1 year' -> 0 ; 'More than 50 years' -> 51 ; ...
    Cột không truyền vào -> tự nhận diện các cột số thường gặp.
    Tuổi ngoài [10, 99] coi là bất thường -> NaN.
    """
    df = df.copy()
    default = ["years_code", "years_code_pro", "age", "work_week_hrs", "comp_total"]
    columns = list(columns) if columns else [c for c in default if c in df.columns]

    replace = {
        "Less than 1 year": "0", "More than 50 years": "51",
        "Younger than 5 years": "4", "Older than 85": "86",
    }
    for c in columns:
        if c not in df.columns:
            continue
        df[c] = pd.to_numeric(df[c].replace(replace), errors="coerce")
    if "age" in df.columns:
        df.loc[(df["age"] < 10) | (df["age"] > 99), "age"] = np.nan
    log.info("Chuẩn hóa cột số: %s", ", ".join(columns) or "(none)")
    return df


# -----------------------------------------------------------------------------
# 4. TÁCH CỘT MULTI-SELECT -> LONG FORMAT
# -----------------------------------------------------------------------------
def normalize_skill(raw: str) -> str:
    """Chuẩn hóa một tên skill: trim + ánh xạ alias. NaN/rỗng -> ''."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s or s.lower() in {"nan", "none", "na", "unknown"}:
        return ""
    return SKILL_ALIASES.get(s.lower(), s)


def split_multiselect_column(df: pd.DataFrame, column_name: str,
                             id_col: str = "respondent_id") -> pd.DataFrame:
    """
    Tách 1 cột multi-select (ngăn cách ';') thành long-format để đếm tần suất.

    Trả về DataFrame: [respondent_id, skill_name, category, source_column]
        - Chuẩn hóa khoảng trắng + alias tên skill.
        - KHÔNG đếm NaN/rỗng.
        - KHÔNG đếm trùng skill trong cùng một respondent.
    """
    if column_name not in df.columns:
        log.warning("Bỏ qua: không có cột %s", column_name)
        return pd.DataFrame(columns=[id_col, "skill_name", "category", "source_column"])

    ids = df[id_col] if id_col in df.columns else pd.RangeIndex(len(df))
    tmp = pd.DataFrame({id_col: ids, "_raw": df[column_name].astype("string")})
    tmp = tmp.dropna(subset=["_raw"])
    tmp["skill_name"] = tmp["_raw"].str.split(";")
    tmp = tmp.explode("skill_name")
    tmp["skill_name"] = tmp["skill_name"].map(normalize_skill)
    tmp = tmp[tmp["skill_name"] != ""]
    tmp = tmp.drop_duplicates(subset=[id_col, "skill_name"])  # 1 skill / người

    tmp["category"] = MULTISELECT_CATEGORY.get(column_name, "other")
    tmp["source_column"] = column_name
    return tmp[[id_col, "skill_name", "category", "source_column"]].reset_index(drop=True)


# -----------------------------------------------------------------------------
# 5. BẢNG TẦN SUẤT (frequency + percentage)
# -----------------------------------------------------------------------------
def calculate_frequency_table(long_df: pd.DataFrame, top_n: Optional[int] = None
                              ) -> pd.DataFrame:
    """
    Từ long-format -> bảng tần suất: [skill_name, count, percentage, category,
    source_column]. percentage = count / số respondent có trong nhóm.
    """
    if long_df.empty:
        return pd.DataFrame(columns=["skill_name", "count", "percentage",
                                     "category", "source_column"])
    id_col = long_df.columns[0]
    denom = long_df[id_col].nunique() or 1
    cat = long_df["category"].iloc[0]
    src = long_df["source_column"].iloc[0]
    out = (long_df.groupby("skill_name")[id_col].nunique()
           .reset_index(name="count")
           .sort_values("count", ascending=False))
    out["percentage"] = (out["count"] / denom * 100).round(1)
    out["category"] = cat
    out["source_column"] = src
    if top_n:
        out = out.head(top_n)
    return out.reset_index(drop=True)


# -----------------------------------------------------------------------------
# 6. SKILL GAP = desired_next_year - worked_with
# -----------------------------------------------------------------------------
def calculate_skill_gap(df: pd.DataFrame, worked_col: str, desired_col: str
                        ) -> pd.DataFrame:
    """
    Tính khoảng tăng trưởng kỹ năng:
        growth_gap = (#muốn dùng năm tới) - (#đang dùng)
        growth_pct = growth_gap / worked * 100
        signal     = Emerging (>+10%) / Stable / Declining (<-10%)
    Trả về bảng đã sort theo growth_gap giảm dần.
    """
    worked = calculate_frequency_table(split_multiselect_column(df, worked_col))
    desired = calculate_frequency_table(split_multiselect_column(df, desired_col))

    g = (worked[["skill_name", "count"]].rename(columns={"count": "worked"})
         .merge(desired[["skill_name", "count"]].rename(columns={"count": "desired_next_year"}),
                on="skill_name", how="outer").fillna(0))
    g["worked"] = g["worked"].astype(int)
    g["desired_next_year"] = g["desired_next_year"].astype(int)
    g["growth_gap"] = g["desired_next_year"] - g["worked"]
    g["growth_pct"] = np.where(g["worked"] > 0,
                               (g["growth_gap"] / g["worked"] * 100).round(1), np.nan)
    g["signal"] = np.select(
        [g["growth_pct"] >= 10, g["growth_pct"] <= -10],
        ["Emerging", "Declining"], default="Stable")
    return g.sort_values("growth_gap", ascending=False).reset_index(drop=True)


# -----------------------------------------------------------------------------
# 7. XUẤT KẾT QUẢ
# -----------------------------------------------------------------------------
def export_clean_data(df: pd.DataFrame, out_path: str | Path) -> Path:
    """Xuất clean dataset ra CSV (utf-8-sig để Excel/Power BI đọc tiếng Việt)."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    log.info("Đã xuất clean data: %s (%d dòng x %d cột)", out, len(df), df.shape[1])
    return out


def export_summary_tables(tables: dict[str, pd.DataFrame], out_dir: str | Path
                          ) -> list[Path]:
    """Xuất nhiều bảng summary ra thư mục (mỗi bảng 1 CSV)."""
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    written = []
    for name, tb in tables.items():
        p = d / f"{name}.csv"
        tb.to_csv(p, index=False, encoding="utf-8-sig")
        written.append(p)
    log.info("Đã xuất %d bảng summary -> %s", len(written), d)
    return written
