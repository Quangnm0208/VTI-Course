"""Tests cho parser của 2 nguồn bổ sung: VietnamWorks (API) & LinkedIn (guest)."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def test_vietnamworks_parse_hit():
    import scrape_vietnamworks as vnw
    hit = {
        "jobTitle": "Senior Data Engineer", "companyName": "VNG",
        "workingLocations": [{"cityName": "Ha Noi"}, {"cityName": "HCM"}],
        "skills": [{"skillName": "Python"}, {"skillName": "SQL"}],
        "salaryMin": 1500, "salaryMax": 2500, "isSalaryVisible": True,
        "jobUrl": "https://www.vietnamworks.com/job/123", "prettySalary": "1,500-2,500 USD",
    }
    j = vnw._parse_hit(hit, date(2026, 6, 16))
    assert j["job_title"] == "Senior Data Engineer"
    assert j["company"] == "VNG"
    assert "Ha Noi" in j["location"] and "HCM" in j["location"]
    assert j["skills"] == "Python;SQL"
    assert j["salary_status"] == "visible"
    assert j["source"] == "VietnamWorks"
    assert j["status"] == "ok"


def test_vietnamworks_hidden_salary():
    import scrape_vietnamworks as vnw
    hit = {"jobTitle": "QA", "companyName": "X", "jobUrl": "https://vnw/1",
           "isSalaryVisible": False}
    j = vnw._parse_hit(hit, date(2026, 6, 16))
    assert j["salary_status"] == "negotiable"
    assert j["salary_min_usd"] is None


def test_linkedin_parse_cards():
    import scrape_linkedin as li
    html = """
    <ul><li>
      <h3 class="base-search-card__title">Backend Developer</h3>
      <h4 class="base-search-card__subtitle"><a>Tiki</a></h4>
      <span class="job-search-card__location">Ho Chi Minh City, Vietnam</span>
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/999?trk=abc">x</a>
    </li></ul>
    """
    jobs = li._parse_cards(html, "backend", date(2026, 6, 16))
    assert len(jobs) == 1
    j = jobs[0]
    assert j["job_title"] == "Backend Developer"
    assert j["company"] == "Tiki"
    assert "Vietnam" in j["location"]
    assert j["source_url"] == "https://www.linkedin.com/jobs/view/999"   # query stripped
    assert j["source"] == "LinkedIn"


def test_linkedin_skips_card_without_title():
    import scrape_linkedin as li
    html = "<ul><li><span>noise</span></li></ul>"
    assert li._parse_cards(html, "x", date(2026, 6, 16)) == []
