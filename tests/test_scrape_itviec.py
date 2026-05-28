"""Tests cho scrape_itviec: phần parser/util không phụ thuộc network."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from bs4 import BeautifulSoup
from scrape_itviec import parse_job_card, parse_salary, today_vn


def test_today_vn_returns_date():
    assert isinstance(today_vn(), date)


def test_parse_salary_range():
    assert parse_salary("1,500 - 2,500 USD") == (1500.0, 2500.0)


def test_parse_salary_single_value():
    assert parse_salary("1500 USD") == (1500.0, 1500.0)


def test_parse_salary_negotiable():
    assert parse_salary("Negotiable") == (None, None)
    assert parse_salary("") == (None, None)


def test_parse_job_card_minimal():
    html = """
    <div class="job-card">
        <h3>Senior Python Developer</h3>
        <a class="company-name" href="/companies/acme">ACME</a>
        <span class="address">Ho Chi Minh</span>
        <span class="salary">1500-2500 USD</span>
        <span class="itag">Python</span>
        <span class="itag">Django</span>
        <a href="/job/1">Apply</a>
    </div>
    """
    card = BeautifulSoup(html, "html.parser").find("div")
    job = parse_job_card(card)

    assert job is not None
    assert job["job_title"] == "Senior Python Developer"
    assert job["company"] == "ACME"
    assert job["location"] == "Ho Chi Minh"
    assert "Python" in job["skills"]
    assert "Django" in job["skills"]
    assert job["salary_min_usd"] == 1500.0
    assert job["salary_max_usd"] == 2500.0
    assert job["source_url"].endswith("/job/1")
    assert job["status"] == "ok"


def test_parse_job_card_returns_none_if_no_title():
    html = "<div class='job-card'><span>empty</span></div>"
    card = BeautifulSoup(html, "html.parser").find("div")
    assert parse_job_card(card) is None
