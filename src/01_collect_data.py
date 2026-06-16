"""
01_collect_data.py — Thu thập tín hiệu NHU CẦU CÔNG NGHỆ từ GitHub REST API.

Đây là NGUỒN DỮ LIỆU THỨ 3 (bên cạnh khảo sát Stack Overflow và scraping ItViec):
số kho mã (repository) công khai theo từng kỹ năng/ngôn ngữ là một proxy đo độ
phổ biến & nhu cầu thực tế của công nghệ trên thị trường mã nguồn mở.

Vì sao GitHub API:
    - Là API công khai, có tài liệu rõ ràng, gọi bằng `requests` (đúng yêu cầu đề).
    - Bổ sung góc nhìn "nguồn cung mã nguồn mở" cho hai nguồn còn lại.
    - Trả về số bản ghi lớn (mỗi repo là 1 bản ghi) -> góp vào mốc tối thiểu.

Xác thực & rate limit:
    - Không token: 10 lượt search/phút, dễ bị giới hạn trên IP dùng chung.
    - Có GITHUB_TOKEN (Actions tự cấp / PAT cá nhân): 30 lượt/phút, ổn định.
    Script tự backoff theo header X-RateLimit-Reset, KHÔNG bịa dữ liệu khi bị chặn.

Đầu ra (data/raw/):
    github_tech_demand.csv   - mỗi dòng: skill, category, repo_count (aggregate)
    github_repos_sample.csv  - mỗi dòng: 1 repo (record-level): skill, repo, stars...

Chạy:
    python src/01_collect_data.py                 # mặc định toàn bộ skill
    GITHUB_TOKEN=ghp_xxx python src/01_collect_data.py
    python src/01_collect_data.py --per-skill 50  # số repo mẫu mỗi skill
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
API = "https://api.github.com/search/repositories"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("collect")

# Danh mục kỹ năng cần đo nhu cầu (đồng bộ với phân tích khảo sát/ItViec).
SKILLS = {
    "programming_language": ["Python", "JavaScript", "TypeScript", "Java", "C#",
                             "Go", "Rust", "Kotlin", "PHP", "Ruby", "Swift", "C++",
                             "Scala", "Dart", "Elixir", "Perl", "R", "Lua", "Haskell",
                             "Clojure", "Julia", "Objective-C", "Groovy"],
    "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
                 "SQLite", "Cassandra", "MariaDB", "DynamoDB", "Neo4j", "CouchDB",
                 "Firebase", "Oracle"],
    "web_framework": ["React", "Vue.js", "Angular", "Django", "Spring", "Express",
                      "Next.js", "FastAPI", "Flask", "Laravel", "Svelte", "NestJS",
                      "Ruby on Rails", "ASP.NET"],
    "cloud_devops": ["Docker", "Kubernetes", "Terraform", "AWS", "Ansible",
                     "Jenkins", "GitLab", "Prometheus", "Grafana", "Helm"],
    "data_ml": ["TensorFlow", "PyTorch", "Pandas", "scikit-learn", "Spark",
                "Airflow", "dbt", "Kafka"],
    "ide_tool": ["Visual Studio Code", "Vim", "Neovim", "Emacs"],
    "mobile": ["Flutter", "React Native", "Android", "iOS"],
}


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json",
         "User-Agent": "vti-course-tech-demand-collector",
         "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _query_for(skill: str, category: str) -> str:
    """Ngôn ngữ -> dùng qualifier language:; còn lại -> tìm theo topic + tên."""
    if category == "programming_language":
        return f"language:{skill}"
    topic = skill.lower().replace(" ", "-").replace(".", "")
    return f"topic:{topic}"


def fetch_skill(session: requests.Session, skill: str, category: str,
                per_skill: int, max_retries: int = 4) -> tuple[int, list[dict]]:
    """
    Gọi GitHub search cho 1 skill. Trả về (repo_count, [repo records]).
    Tự backoff khi gặp 403 rate limit (đọc X-RateLimit-Reset).
    """
    params = {"q": _query_for(skill, category), "sort": "stars",
              "order": "desc", "per_page": min(per_skill, 100)}
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(API, params=params, headers=_headers(), timeout=20)
        except requests.RequestException as err:
            log.warning("  [%s] lỗi mạng: %s", skill, err)
            time.sleep(2 * attempt)
            continue

        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            recs = [{
                "skill": skill, "category": category,
                "repo": it.get("full_name"), "stars": it.get("stargazers_count"),
                "forks": it.get("forks_count"), "language": it.get("language"),
                "pushed_at": (it.get("pushed_at") or "")[:10],
            } for it in items]
            return int(data.get("total_count", 0)), recs

        if r.status_code in (403, 429):
            reset = r.headers.get("X-RateLimit-Reset")
            wait = max(2, min(60, int(reset) - int(time.time()))) if reset else 5 * attempt
            log.warning("  [%s] rate limited (HTTP %s) -> chờ %ds (lần %d)",
                        skill, r.status_code, wait, attempt)
            time.sleep(wait)
            continue

        log.warning("  [%s] HTTP %s", skill, r.status_code)
        break
    return -1, []   # -1 = không lấy được (không bịa)


def main() -> int:
    ap = argparse.ArgumentParser(description="Thu thập nhu cầu công nghệ qua GitHub API")
    ap.add_argument("--per-skill", type=int, default=30, help="Số repo mẫu mỗi skill (<=100)")
    ap.add_argument("--out-dir", default=str(RAW))
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    session = requests.Session()
    demand_rows, repo_rows = [], []
    ok = 0
    flat = [(s, c) for c, lst in SKILLS.items() for s in lst]
    log.info("Bắt đầu thu thập %d skill từ GitHub API (token=%s)",
             len(flat), "có" if os.environ.get("GITHUB_TOKEN") else "không")

    for i, (skill, category) in enumerate(flat, 1):
        count, recs = fetch_skill(session, skill, category, args.per_skill)
        if count >= 0:
            demand_rows.append({"collected_date": today, "skill": skill,
                                "category": category, "repo_count": count,
                                "sample_size": len(recs), "source": "GitHub"})
            for rec in recs:
                rec["collected_date"] = today
                rec["source"] = "GitHub"
            repo_rows.extend(recs)
            ok += 1
            log.info("[%2d/%d] %-22s %-20s repo_count=%s (+%d records)",
                     i, len(flat), skill, category, f"{count:,}", len(recs))
        time.sleep(1.0)   # nhẹ nhàng với API

    if not demand_rows:
        log.error("Không thu được dữ liệu nào (có thể bị rate limit trên IP dùng chung). "
                  "Hãy đặt GITHUB_TOKEN rồi chạy lại — KHÔNG ghi dữ liệu giả.")
        return 2

    # Ghi 2 file: aggregate (demand) + record-level (repos)
    demand_path = out / "github_tech_demand.csv"
    with demand_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["collected_date", "skill", "category",
                                          "repo_count", "sample_size", "source"])
        w.writeheader(); w.writerows(demand_rows)

    repo_path = out / "github_repos_sample.csv"
    if repo_rows:
        with repo_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["collected_date", "source", "skill",
                                              "category", "repo", "stars", "forks",
                                              "language", "pushed_at"])
            w.writeheader(); w.writerows(repo_rows)

    log.info("HOÀN TẤT: %d/%d skill, %d repo records -> %s",
             ok, len(flat), len(repo_rows), out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
