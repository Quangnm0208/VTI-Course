"""Tests cho data_quality: kiểm tra logic check trả về đúng status."""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from data_quality import (
    check_anomalies, check_data_age, check_ok_ratio,
    check_skill_coverage, check_total_jobs,
)


def _row(scrape_date: str, status: str = "ok", skills: str = "Python",
         salary_min: float | str = 1000, salary_max: float | str = 2000) -> dict:
    return {
        "scrape_date":    scrape_date,
        "source_url":     "https://itviec.com/job/1",
        "status":         status,
        "skills":         skills,
        "salary_min_usd": salary_min,
        "salary_max_usd": salary_max,
    }


def test_total_jobs_pass():
    today = date.today().isoformat()
    rows = [_row(today) for _ in range(100)]
    assert check_total_jobs(rows)["status"] == "PASS"


def test_total_jobs_warn_when_below_threshold():
    today = date.today().isoformat()
    rows = [_row(today) for _ in range(5)]
    assert check_total_jobs(rows)["status"] == "WARN"


def test_ok_ratio_fail_when_csv_empty():
    assert check_ok_ratio([])["status"] == "FAIL"


def test_ok_ratio_warn_when_too_many_pending():
    rows = [_row("2026-05-28", status="pending") for _ in range(10)]
    rows += [_row("2026-05-28", status="ok") for _ in range(2)]
    assert check_ok_ratio(rows)["status"] == "WARN"


def test_skill_coverage_warn_when_skills_missing():
    rows = [_row("2026-05-28", skills="") for _ in range(10)]
    assert check_skill_coverage(rows)["status"] == "WARN"


def test_data_age_fail_when_stale():
    old = (date.today() - timedelta(days=30)).isoformat()
    rows = [_row(old)]
    assert check_data_age(rows)["status"] == "FAIL"


def test_data_age_pass_when_fresh():
    today = date.today().isoformat()
    rows = [_row(today)]
    assert check_data_age(rows)["status"] == "PASS"


def test_anomalies_detects_future_date():
    future = (date.today() + timedelta(days=5)).isoformat()
    rows = [_row(future)]
    assert check_anomalies(rows)["status"] == "WARN"


def test_anomalies_detects_negative_salary():
    today = date.today().isoformat()
    rows = [_row(today, salary_min=-100, salary_max=200)]
    assert check_anomalies(rows)["status"] == "WARN"


def test_anomalies_pass_when_clean():
    today = date.today().isoformat()
    rows = [_row(today)]
    assert check_anomalies(rows)["status"] == "PASS"
