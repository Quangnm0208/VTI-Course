"""
03_analyze_data.py — Pipeline phân tích: raw survey -> clean data + summary tables.

Luồng (theo yêu cầu đề bài):
    load_data -> standardize_column_names -> clean_numeric_columns
              -> split_multiselect_column / calculate_frequency_table
              -> calculate_skill_gap -> export_clean_data / export_summary_tables

Đầu vào (ưu tiên theo thứ tự):
    data/raw/Final Project.csv  hoặc  data/raw/final_project.csv
Nếu KHÔNG có file raw, script dùng lại bộ
số liệu tổng hợp đã chốt trong analysis/market_insight_data.py (chính là kết
quả tính từ notebook trên dữ liệu thật) để vẫn xuất được các bảng summary.

Đầu ra: data/processed/
    clean_it_skills_data.csv          (chỉ khi có raw)
    language_summary.csv
    database_summary.csv
    ide_summary.csv
    emerging_skills_summary.csv

Chạy:
    python src/03_analyze_data.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "analysis"))

import utils  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("analyze")

RAW_CANDIDATES = [
    ROOT / "data" / "raw" / "Final Project.csv",
    ROOT / "data" / "raw" / "final_project.csv",
    ROOT / "data" / "raw" / "survey_raw.csv",
]
PROCESSED = ROOT / "data" / "processed"

# Các cột "clean dataset" cần giữ (đề bài liệt kê).
CLEAN_COLUMNS = [
    "respondent_id", "country", "employment", "dev_type", "years_code",
    "years_code_pro", "language_worked_with", "language_desire_next_year",
    "database_worked_with", "database_desire_next_year", "platform_worked_with",
    "platform_desire_next_year", "webframe_worked_with", "webframe_desire_next_year",
    "misc_tech_worked_with", "misc_tech_desire_next_year", "dev_environment",
    "operating_system", "comp_total", "age", "work_week_hrs",
]


def _find_raw() -> Path | None:
    return next((p for p in RAW_CANDIDATES if p.exists()), None)


# -----------------------------------------------------------------------------
# Nhánh A: có file raw -> chạy pipeline thật end-to-end
# -----------------------------------------------------------------------------
def run_from_raw(raw_path: Path) -> None:
    log.info("=== Chạy pipeline THẬT từ raw: %s ===", raw_path.name)
    df = utils.load_data(raw_path)
    df = utils.standardize_column_names(df)
    df = utils.clean_numeric_columns(df)

    # 1) Clean dataset (giữ các cột chuẩn + khử trùng theo respondent_id)
    keep = [c for c in CLEAN_COLUMNS if c in df.columns]
    clean = df[keep].copy()
    if "respondent_id" in clean.columns:
        clean = clean.drop_duplicates(subset=["respondent_id"])
    # Điền thiếu: text -> 'Unknown', numeric -> median
    for c in clean.columns:
        if clean[c].dtype == object:
            clean[c] = clean[c].fillna("Unknown")
        else:
            clean[c] = clean[c].fillna(clean[c].median())
    utils.export_clean_data(clean, PROCESSED / "clean_it_skills_data.csv")

    # 2) Bảng tần suất theo từng nhóm
    lang = utils.calculate_frequency_table(
        utils.split_multiselect_column(df, "language_worked_with"), top_n=15)
    db = utils.calculate_frequency_table(
        utils.split_multiselect_column(df, "database_worked_with"), top_n=15)
    ide = utils.calculate_frequency_table(
        utils.split_multiselect_column(df, "dev_environment"), top_n=15)

    # 3) Skill gap (emerging)
    emerging = utils.calculate_skill_gap(
        df, "language_worked_with", "language_desire_next_year")

    utils.export_summary_tables({
        "language_summary": lang,
        "database_summary": db,
        "ide_summary": ide,
        "emerging_skills_summary": emerging,
    }, PROCESSED)
    log.info("HOÀN TẤT (raw). Xem data/processed/")


# -----------------------------------------------------------------------------
# Nhánh B: KHÔNG có raw -> dùng số liệu tổng hợp đã chốt
# -----------------------------------------------------------------------------
def run_from_aggregates() -> None:
    log.warning("Không tìm thấy 'Final Project.csv' trong data/raw/. "
                "Dùng bộ số liệu tổng hợp đã chốt (analysis/market_insight_data.py) "
                "— đây là kết quả đã tính sẵn từ dữ liệu khảo sát gốc.")
    import market_insight_data as M  # noqa: E402

    lang = M.language_signal()
    db = M.database_signal()
    ide = M.ide_overall()

    language_summary = (lang[["language", "worked", "growth_pct", "signal"]]
                        .rename(columns={"language": "skill_name", "worked": "count"}))
    language_summary["category"] = "programming_language"
    database_summary = (db[["database", "worked", "growth_pct", "signal"]]
                        .rename(columns={"database": "skill_name", "worked": "count"}))
    database_summary["category"] = "database"
    ide_summary = (ide.rename(columns={"ide": "skill_name",
                                       "developer_count": "count",
                                       "usage_pct": "percentage"}))
    ide_summary["category"] = "ide"
    emerging = (lang.rename(columns={"language": "skill_name",
                                     "worked": "worked",
                                     "net_change": "growth_gap"})
                [["skill_name", "worked", "desired_next_year", "growth_gap",
                  "growth_pct", "signal"]]
                .sort_values("growth_gap", ascending=False))

    utils.export_summary_tables({
        "language_summary": language_summary,
        "database_summary": database_summary,
        "ide_summary": ide_summary,
        "emerging_skills_summary": emerging,
    }, PROCESSED)
    log.info("HOÀN TẤT (aggregate fallback). Xem data/processed/")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    raw = _find_raw()
    if raw:
        run_from_raw(raw)
    else:
        run_from_aggregates()


if __name__ == "__main__":
    main()
