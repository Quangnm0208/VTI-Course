"""
market_insight_data.py — Bảng số liệu phân tích đã chốt (single source of truth).

Toàn bộ con số trong file này được tính trực tiếp từ khảo sát Stack Overflow
(Final Project.csv, 11.552 developer / 135 quốc gia) trong notebook
`vti_hr_curriculum_market_insight.ipynb`. Tách riêng ra đây để Dashboard, SQL,
PowerPoint và Narrative summary CÙNG dùng một bộ số -> không lệch nhau.

Mỗi hàm trả về một pandas.DataFrame sạch, tên cột snake_case.
"""
from __future__ import annotations

import pandas as pd


# -----------------------------------------------------------------------------
# 0. Tổng quan dữ liệu (KPI cards)
# -----------------------------------------------------------------------------
def dataset_overview() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Total respondents", 11552, "Đủ lớn để đọc tín hiệu thị trường toàn cầu."),
            ("Countries covered", 135, "Benchmark toàn cầu, không chỉ một thị trường."),
            ("Viet Nam responses", 12, "Mẫu VN nhỏ -> phải kiểm chứng nội địa."),
            ("Median salary USD", 57844, "Dùng trung vị làm mốc tham chiếu lương."),
            ("Median professional coding years", 5, "Mẫu thiên về dev chuyên nghiệp tầm trung."),
            ("Employed full-time percentage", 96.2, "Tín hiệu phù hợp tuyển dụng chính quy."),
            ("Avg languages worked per respondent", 5.2, "Dev hiện đại là polyglot."),
            ("Avg languages desired per respondent", 4.9, "Ứng viên muốn học đa kỹ năng."),
        ],
        columns=["metric", "value", "hr_meaning"],
    )


# -----------------------------------------------------------------------------
# 1. Tín hiệu ngôn ngữ lập trình (đang dùng vs muốn dùng năm sau)
# -----------------------------------------------------------------------------
def language_signal() -> pd.DataFrame:
    rows = [
        # language, worked, desired_next_year, net_change, growth_pct, desired_market_pct, signal
        ("JavaScript", 8805, 6715, -2090, -23.7, 58.1, "Declining"),
        ("HTML/CSS", 7920, 5398, -2522, -31.8, 46.7, "Declining"),
        ("Python", 4611, 5309, 698, 15.1, 46.0, "Stable"),
        ("SQL", 7213, 5094, -2119, -29.4, 44.1, "Declining"),
        ("TypeScript", 3269, 4140, 871, 26.6, 35.8, "Emerging"),
        ("C#", 4346, 3639, -707, -16.3, 31.5, "Stable"),
        ("Bash/Shell/PowerShell", 4694, 3135, -1559, -33.2, 27.1, "Declining"),
        ("Java", 4556, 2987, -1569, -34.4, 25.9, "Declining"),
        ("Go", 1133, 2813, 1680, 148.3, 24.4, "Emerging"),
        ("Kotlin", 754, 1907, 1153, 152.9, 16.5, "Emerging"),
        ("C++", 1964, 1645, -319, -16.2, 14.2, "Stable"),
        ("Rust", 328, 1540, 1212, 369.5, 13.3, "Emerging"),
        ("PHP", 2950, 1475, -1475, -50.0, 12.8, "Declining"),
        ("WebAssembly", 136, 1417, 1281, 941.9, 12.3, "Emerging"),
        ("C", 1601, 1040, -561, -35.0, 9.0, "Declining"),
    ]
    return pd.DataFrame(
        rows,
        columns=["language", "worked", "desired_next_year", "net_change",
                 "growth_pct", "desired_market_pct", "signal"],
    )


# -----------------------------------------------------------------------------
# 2. Tín hiệu cơ sở dữ liệu
# -----------------------------------------------------------------------------
def database_signal() -> pd.DataFrame:
    rows = [
        ("PostgreSQL", 4153, 4386, 233, 5.6, 38.0, "Stable"),
        ("MongoDB", 3058, 3703, 645, 21.1, 32.1, "Emerging"),
        ("Redis", 2536, 3385, 849, 33.5, 29.3, "Emerging"),
        ("MySQL", 5549, 3328, -2221, -40.0, 28.8, "Declining"),
        ("Elasticsearch", 1980, 2898, 918, 46.4, 25.1, "Emerging"),
        ("Microsoft SQL Server", 4170, 2747, -1423, -34.1, 23.8, "Declining"),
        ("SQLite", 3292, 2465, -827, -25.1, 21.3, "Declining"),
        ("Firebase", 1343, 1679, 336, 25.0, 14.5, "Emerging"),
        ("MariaDB", 1724, 1400, -324, -18.8, 12.1, "Stable"),
        ("DynamoDB", 839, 1056, 217, 25.9, 9.1, "Emerging"),
        ("Cassandra", 403, 1023, 620, 153.8, 8.9, "Emerging"),
        ("Oracle", 1761, 881, -880, -50.0, 7.6, "Declining"),
    ]
    return pd.DataFrame(
        rows,
        columns=["database", "worked", "desired_next_year", "net_change",
                 "growth_pct", "desired_market_pct", "signal"],
    )


# -----------------------------------------------------------------------------
# 3. IDE theo vai trò (top 3 mỗi vai trò)
# -----------------------------------------------------------------------------
def ide_by_role() -> pd.DataFrame:
    rows = [
        ("Back-end Developer", 1, "Visual Studio Code", 3575),
        ("Back-end Developer", 2, "Visual Studio", 2311),
        ("Back-end Developer", 3, "Notepad++", 2027),
        ("Data Scientist / ML", 1, "IPython / Jupyter", 390),
        ("Data Scientist / ML", 2, "Visual Studio Code", 373),
        ("Data Scientist / ML", 3, "PyCharm", 273),
        ("Data/BI Analyst", 1, "Visual Studio Code", 408),
        ("Data/BI Analyst", 2, "Notepad++", 350),
        ("Data/BI Analyst", 3, "Visual Studio", 346),
        ("DevOps Specialist", 1, "Visual Studio Code", 996),
        ("DevOps Specialist", 2, "Vim", 649),
        ("DevOps Specialist", 3, "Visual Studio", 540),
        ("Front-end Developer", 1, "Visual Studio Code", 2634),
        ("Front-end Developer", 2, "Visual Studio", 1476),
        ("Front-end Developer", 3, "Notepad++", 1265),
    ]
    return pd.DataFrame(rows, columns=["role", "rank", "ide", "developer_count"])


def ide_overall() -> pd.DataFrame:
    """Tổng hợp IDE toàn thị trường (gộp từ ma trận vai trò + tín hiệu chung)."""
    rows = [
        ("Visual Studio Code", 8559, 55.0),
        ("Visual Studio", 4732, 30.4),
        ("Notepad++", 4642, 29.8),
        ("IntelliJ", 3957, 25.4),
        ("Vim", 3382, 21.7),
        ("Android Studio", 2314, 14.9),
        ("PyCharm", 2237, 14.4),
        ("Sublime Text", 2201, 14.1),
        ("IPython / Jupyter", 2010, 12.9),
        ("Eclipse", 1789, 11.5),
    ]
    return pd.DataFrame(rows, columns=["ide", "developer_count", "usage_pct"])


# -----------------------------------------------------------------------------
# 4. Lương theo ngôn ngữ (USD, trung vị)
# -----------------------------------------------------------------------------
def salary_by_language() -> pd.DataFrame:
    rows = [
        ("Clojure", 152, 93404, 114203, 44.1),
        ("Go", 1060, 80000, 98923, 24.8),
        ("Scala", 461, 79163, 98884, 24.7),
        ("Ruby", 1094, 75000, 94376, 19.0),
        ("Elixir", 169, 71966, 89015, 12.3),
        ("Rust", 311, 70000, 88382, 11.5),
        ("Bash/Shell/PowerShell", 4417, 68745, 89946, 13.5),
        ("Objective-C", 483, 64115, 87429, 10.3),
        ("Python", 4293, 64000, 85750, 8.2),
        ("R", 552, 63016, 85477, 7.8),
        ("Swift", 668, 60674, 81501, 2.8),
        ("TypeScript", 3012, 60173, 80456, 3.5),
        ("C#", 3993, 59112, 79957, 1.6),
        ("JavaScript", 8136, 58000, 79063, 0.0),
        ("SQL", 6687, 58284, 78852, -0.7),
        ("Java", 4168, 53437, 75838, -7.6),
        ("PHP", 2720, 43296, 66879, -25.2),
    ]
    return pd.DataFrame(
        rows,
        columns=["language", "developer_count", "median_salary",
                 "mean_salary", "mean_vs_global_pct"],
    )


# -----------------------------------------------------------------------------
# 5. Ưu tiên tuyển dụng theo vai trò
# -----------------------------------------------------------------------------
def role_priority() -> pd.DataFrame:
    rows = [
        ("Full-stack Developer", 6928, 59000, 72.9, "Priority 1"),
        ("Back-end Developer", 6290, 56715, 65.9, "Priority 2"),
        ("DevOps Specialist", 1639, 71036, 46.1, "Priority 2"),
        ("Front-end Developer", 3920, 53437, 45.2, "Priority 2"),
        ("Product/BA", 1179, 61650, 33.3, "Priority 3"),
        ("Data/BI Analyst", 802, 61872, 30.8, "Priority 3"),
        ("Data Scientist / ML", 803, 60000, 28.9, "Priority 3"),
        ("Mobile Developer", 1959, 46152, 23.5, "Priority 3"),
    ]
    return pd.DataFrame(
        rows,
        columns=["role", "developer_count", "median_salary",
                 "hiring_priority_score", "priority_band"],
    )


# -----------------------------------------------------------------------------
# 6. Phân bố theo quốc gia (top)
# -----------------------------------------------------------------------------
def country_distribution() -> pd.DataFrame:
    rows = [
        ("United States", 3173, 27.5),
        ("India", 911, 7.9),
        ("United Kingdom", 841, 7.3),
        ("Germany", 715, 6.2),
        ("Canada", 442, 3.8),
        ("France", 339, 2.9),
        ("Brazil", 328, 2.8),
        ("Australia", 287, 2.5),
    ]
    return pd.DataFrame(rows, columns=["country", "count", "pct"])


# -----------------------------------------------------------------------------
# 7. JD keyword map (must-have vs growth) theo track
# -----------------------------------------------------------------------------
def jd_keyword_map() -> pd.DataFrame:
    rows = [
        ("Full-stack Developer", "Full-stack Engineering",
         "JavaScript, TypeScript, React, SQL, Git", "Node.js, PostgreSQL, Docker, Cloud"),
        ("Back-end Developer", "Backend Engineering",
         "Java, Spring, SQL, PostgreSQL, API, Git", "Go, TypeScript, Docker, Kubernetes, Redis"),
        ("DevOps Specialist", "Cloud and DevOps",
         "Linux, Docker, Kubernetes, AWS, CI/CD", "Kubernetes, Terraform, Cloud, Monitoring"),
        ("Front-end Developer", "Frontend Engineering",
         "JavaScript, HTML/CSS, React, TypeScript, Git", "TypeScript, Vue.js, Testing, API"),
        ("Product/BA", "Product and Business Analysis",
         "Requirement Analysis, SQL, Stakeholder, User Story", "Data-driven Product, Experiment, Dashboard"),
        ("Data/BI Analyst", "Data Analytics",
         "SQL, Python, Excel, Power BI, Data Visualization", "PostgreSQL, Python, Dashboard, Business Metrics"),
        ("Data Scientist / ML", "Data Science and ML",
         "Python, SQL, Statistics, Machine Learning, Jupyter", "PyTorch, TensorFlow, Cloud, MLOps"),
        ("Mobile Developer", "Mobile Engineering",
         "Kotlin, Android Studio, Swift, Xcode, API", "Kotlin, Flutter, Mobile CI/CD"),
    ]
    return pd.DataFrame(
        rows,
        columns=["role", "hiring_track", "must_have_keywords", "growth_keywords"],
    )


# -----------------------------------------------------------------------------
# 8. Lộ trình đào tạo 4 tuần
# -----------------------------------------------------------------------------
def training_roadmap() -> pd.DataFrame:
    rows = [
        ("Week 1", "VS Code, Git and working environment", "All technical roles",
         "Tạo nền công cụ chung, rút ngắn onboarding."),
        ("Week 2", "SQL and PostgreSQL foundation", "Data, Backend, Full-stack",
         "SQL là kỹ năng nền xuyên suốt mọi vai trò."),
        ("Week 3", "Role-specific stack", "Backend, Frontend, Mobile, Data, DevOps",
         "Chuyên sâu theo track ưu tiên tuyển dụng."),
        ("Week 4", "Project, interview and communication review", "All technical roles",
         "Bằng chứng dự án + chấm theo rubric 100 điểm."),
    ]
    return pd.DataFrame(rows, columns=["phase", "training_block", "target_roles", "hr_reason"])


# -----------------------------------------------------------------------------
# 9. Khung chấm phỏng vấn 100 điểm
# -----------------------------------------------------------------------------
def interview_rubric() -> pd.DataFrame:
    rows = [
        ("Core technical skill", 25, "Ngôn ngữ/stack chính theo vai trò."),
        ("Data and database thinking", 20, "SQL, schema, PostgreSQL/NoSQL."),
        ("Project evidence", 20, "Dự án, portfolio, giải quyết bài toán nghiệp vụ."),
        ("Tooling and workflow", 15, "VS Code, Git, debug, môi trường."),
        ("Problem solving", 10, "Tư duy thuật toán/logic."),
        ("Communication", 10, "Trình bày, làm việc nhóm."),
    ]
    return pd.DataFrame(rows, columns=["assessment_area", "weight_pct", "what_to_test"])


# -----------------------------------------------------------------------------
# 10. 3 kiến nghị chiến lược (đề bài yêu cầu >= 3)
# -----------------------------------------------------------------------------
def strategic_recommendations() -> pd.DataFrame:
    rows = [
        ("Ngắn hạn (quý này)",
         "Mở track Cloud & DevOps (Docker/Kubernetes/AWS) + Python for Data",
         "Cloud/DevOps median salary cao nhất ($71k) và Elasticsearch/Redis tăng "
         "trưởng 30-46%. Cầu lớn, cung còn ít -> học viên ra trường có việc ngay."),
        ("Trung hạn (6 tháng)",
         "Đưa TypeScript, Go, Kotlin, Rust vào lộ trình nâng cao",
         "Net-change muốn-dùng dương lớn: Rust +370%, Kotlin +153%, Go +148%, "
         "TypeScript +27%. Đón đầu xu hướng 2-3 năm tới."),
        ("Dài hạn (1 năm)",
         "Lấy PostgreSQL + VS Code + Git làm nền chung cho mọi track và duy trì "
         "pipeline scraping ItViec để tái phân tích mỗi quý",
         "VS Code thống lĩnh ~55% mọi vai trò; PostgreSQL vừa phổ biến vừa tăng. "
         "Thị trường đổi 6 tháng/lần -> cần dữ liệu cập nhật liên tục."),
    ]
    return pd.DataFrame(rows, columns=["horizon", "recommendation", "evidence"])


# -----------------------------------------------------------------------------
# Tập hợp tất cả bảng (tiện cho generate)
# -----------------------------------------------------------------------------
ALL_TABLES = {
    "dataset_overview": dataset_overview,
    "language_signal": language_signal,
    "database_signal": database_signal,
    "ide_by_role": ide_by_role,
    "ide_overall": ide_overall,
    "salary_by_language": salary_by_language,
    "role_priority": role_priority,
    "country_distribution": country_distribution,
    "jd_keyword_map": jd_keyword_map,
    "training_roadmap": training_roadmap,
    "interview_rubric": interview_rubric,
    "strategic_recommendations": strategic_recommendations,
}
