"""Tests cho src/utils.py — pipeline làm sạch & phân tích kỹ năng."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import utils  # noqa: E402


def _sample():
    return pd.DataFrame({
        "Respondent": [1, 2, 3, 2],          # 2 bị lặp -> phải khử
        "Country": ["Vietnam", "US", "India", "US"],
        "YearsCodePro": ["Less than 1 year", "10", "5", "10"],
        "Age": [21, 35, 200, 35],            # 200 -> bất thường -> NaN
        "LanguageWorkedWith": ["Python;SQL;js", "Java;SQL", "python3;Go", "Java;SQL"],
        "LanguageDesireNextYear": ["Python;Rust", "Go;Kotlin", "Rust;Go", None],
    })


def test_standardize_column_names():
    df = utils.standardize_column_names(_sample())
    assert "respondent_id" in df.columns
    assert "language_worked_with" in df.columns
    assert "years_code_pro" in df.columns


def test_clean_numeric_columns_handles_labels_and_outliers():
    df = utils.standardize_column_names(_sample())
    df = utils.clean_numeric_columns(df)
    assert df["years_code_pro"].iloc[0] == 0  # "Less than 1 year" -> 0
    assert pd.isna(df["age"].iloc[2])         # 200 -> NaN


def test_split_multiselect_dedup_and_alias():
    df = utils.standardize_column_names(_sample())
    long = utils.split_multiselect_column(df, "language_worked_with")
    # alias: js -> JavaScript, python3 -> Python
    assert "JavaScript" in set(long["skill_name"])
    assert "Python" in set(long["skill_name"])
    # respondent 2 lặp dòng Java;SQL nhưng chỉ đếm 1 lần / người
    r2 = long[long["respondent_id"] == 2]
    assert r2["skill_name"].is_unique


def test_frequency_table_percentage():
    df = utils.standardize_column_names(_sample())
    long = utils.split_multiselect_column(df, "language_worked_with")
    freq = utils.calculate_frequency_table(long)
    assert {"skill_name", "count", "percentage", "category"} <= set(freq.columns)
    # SQL xuất hiện ở 2/3 respondent duy nhất -> 66.7%
    sql_row = freq[freq["skill_name"] == "SQL"].iloc[0]
    assert sql_row["count"] == 2
    assert abs(sql_row["percentage"] - 66.7) < 0.1


def test_skill_gap_signal():
    df = utils.standardize_column_names(_sample())
    gap = utils.calculate_skill_gap(df, "language_worked_with", "language_desire_next_year")
    assert {"growth_gap", "growth_pct", "signal"} <= set(gap.columns)
    # Rust chỉ có ở desired -> growth_gap dương
    rust = gap[gap["skill_name"] == "Rust"].iloc[0]
    assert rust["growth_gap"] > 0


def test_export_clean_data(tmp_path):
    df = utils.standardize_column_names(_sample())
    out = utils.export_clean_data(df, tmp_path / "clean.csv")
    assert out.exists()
    assert len(pd.read_csv(out)) == len(df)
