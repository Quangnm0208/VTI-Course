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


# ---- Fix: lương bị ẩn + URL sign_in + tiền tệ VND --------------------------
from scrape_itviec import (  # noqa: E402
    canonical_job_url, detect_currency, to_usd, salary_status_from_text,
    company_from_slug,
)


def test_canonical_url_reconstructs_from_signin():
    """Link 'sign_in?job=slug' phải được tái tạo thành /it/slug (không lưu nhầm)."""
    u = ("https://itviec.com/sign_in?job=hcm-senior-data-engineer-one-mount-1651"
         "&job_index=1&view_salary_source=search_page")
    assert canonical_job_url(u) == "https://itviec.com/it/hcm-senior-data-engineer-one-mount-1651"


def test_canonical_url_keeps_normal_link():
    assert canonical_job_url("/it/backend-dev-1") == "https://itviec.com/it/backend-dev-1"


def test_salary_status_login_required():
    assert salary_status_from_text("Sign in to view salary") == "login_required"
    assert salary_status_from_text("Negotiable") == "negotiable"
    assert salary_status_from_text("1500 USD") == "visible"


def test_parse_salary_vnd_and_upto():
    assert parse_salary("20,000,000 - 35,000,000 VND") == (20000000.0, 35000000.0)
    assert parse_salary("Up to 3,000 USD") == (None, 3000.0)
    assert parse_salary("From 1,000 USD") == (1000.0, None)


def test_currency_and_conversion():
    assert detect_currency("20,000,000 VND") == "VND"
    assert detect_currency("1500 USD") == "USD"
    # 25,000,000 VND / 25000 = 1000 USD (tỷ giá mặc định)
    assert to_usd(25_000_000, "VND") == 1000.0
    assert to_usd(1500, "USD") == 1500


def test_job_card_signin_salary_marks_login_required():
    html = """
    <div class="job-card">
        <h3>(HCM) Senior Data Engineer</h3>
        <a href="/companies/one-mount">One Mount</a>
        <a href="/sign_in?job=hcm-senior-data-engineer-one-mount-1651&view_salary_source=search_page">Sign in to view salary</a>
        <span class="salary">Sign in to view salary</span>
        <span class="itag">Python</span>
    </div>
    """
    card = BeautifulSoup(html, "html.parser").find("div")
    job = parse_job_card(card)
    assert job["company"] == "One Mount"
    assert job["source_url"] == "https://itviec.com/it/hcm-senior-data-engineer-one-mount-1651"
    assert job["salary_status"] == "login_required"
    assert job["salary_min_usd"] is None
