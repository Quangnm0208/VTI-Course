"""Tests cho parse_job_detail: bóc salary từ JSON-LD."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from scrape_itviec import parse_job_detail


def test_parse_jsonld_salary_range():
    html = """
    <html><head>
    <script type="application/ld+json">
    {
        "@type": "JobPosting",
        "title": "Senior Python",
        "baseSalary": {
            "currency": "USD",
            "value": {"minValue": 1500, "maxValue": 2500, "@type": "QuantitativeValue"}
        }
    }
    </script>
    </head></html>
    """
    result = parse_job_detail(html)
    assert result["salary_min_usd"] == 1500
    assert result["salary_max_usd"] == 2500
    assert result["salary_currency"] == "USD"
    assert result["salary_source"] == "json-ld"


def test_parse_jsonld_in_list():
    html = """
    <script type="application/ld+json">
    [
        {"@type": "Organization", "name": "ACME"},
        {"@type": "JobPosting",
         "baseSalary": {"currency": "VND",
                        "value": {"minValue": 20000000, "maxValue": 30000000}}}
    ]
    </script>
    """
    result = parse_job_detail(html)
    assert result["salary_min_usd"] == 20000000
    assert result["salary_currency"] == "VND"


def test_parse_dom_fallback_when_no_jsonld():
    html = '<html><span class="salary">1000 - 2000 USD</span></html>'
    result = parse_job_detail(html)
    assert result["salary_min_usd"] == 1000.0
    assert result["salary_max_usd"] == 2000.0
    assert result["salary_source"] == "dom-text"


def test_parse_ignores_sign_in_text():
    html = '<html><span class="salary">Sign in to view salary</span></html>'
    result = parse_job_detail(html)
    assert result["salary_min_usd"] is None
    assert result["salary_source"] == "none"


def test_parse_returns_none_when_no_data():
    html = "<html><body></body></html>"
    result = parse_job_detail(html)
    assert result["salary_min_usd"] is None
    assert result["salary_source"] == "none"


def test_parse_company_from_companies_link():
    """Test fix mới: parser bóc được company từ link /companies/SLUG."""
    from bs4 import BeautifulSoup
    from scrape_itviec import parse_job_card

    html = """
    <div class="job-card">
        <h3>Backend Developer</h3>
        <a href="/companies/fpt-software">FPT Software</a>
        <a href="/it-jobs/backend-1">Detail</a>
        <span class="address">HCM</span>
    </div>
    """
    card = BeautifulSoup(html, "html.parser").find("div")
    job = parse_job_card(card)
    assert job["company"] == "FPT Software"
    assert "/it-jobs/" in job["source_url"]


def test_parse_company_fallback_to_slug():
    """Nếu link company không có text -> derive từ slug URL."""
    from bs4 import BeautifulSoup
    from scrape_itviec import parse_job_card

    html = """
    <div class="job-card">
        <h3>Frontend Dev</h3>
        <a href="/companies/tiki-corp"><img/></a>
        <a href="/it-jobs/fe-1">Detail</a>
    </div>
    """
    card = BeautifulSoup(html, "html.parser").find("div")
    job = parse_job_card(card)
    assert job["company"] == "Tiki Corp"
