"""
build_sql.py — Sinh sql/analysis_queries.sql từ bộ số liệu đã chốt.

Tạo file SQL chuẩn theo yêu cầu đề bài (mục 8):
  - CREATE TABLE respondents / respondent_profile / skill_usage (long-format)
  - Thêm skill_signal_summary chứa SỐ LIỆU THẬT (tổng hợp) để các truy vấn
    phân tích trả về đúng xếp hạng mà không cần nạp 11.552 dòng.
  - INSERT mẫu cho skill_usage (DEMO chạy độc lập) + INSERT thật cho summary.
  - SELECT: top current/desired language, top database, top IDE, emerging gap,
    so sánh theo quốc gia & kinh nghiệm.
Dialect: SQLite (chú thích cách port sang MySQL/PostgreSQL).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
import market_insight_data as M  # noqa: E402

OUT = ROOT / "sql" / "analysis_queries.sql"


def esc(s: str) -> str:
    return str(s).replace("'", "''")


def main() -> None:
    lang = M.language_signal()
    db = M.database_signal()
    ide = M.ide_overall()
    sal = M.salary_by_language()
    role = M.role_priority()

    L = []
    L.append("-- " + "=" * 75)
    L.append("-- VTI ACADEMY — FINAL PROJECT | analysis_queries.sql")
    L.append("-- Phân tích kỹ năng IT từ khảo sát Stack Overflow (11.552 dev / 135 nước).")
    L.append("-- Cấu trúc long-format 'skill_usage' + bảng tổng hợp số liệu THẬT.")
    L.append("-- Dialect: SQLite. (MySQL: bỏ 'IF NOT EXISTS' cho INDEX; PostgreSQL: ok.)")
    L.append("-- File này được sinh bởi analysis/build_sql.py để số liệu luôn khớp")
    L.append("-- dashboard, notebook và slide. KHÔNG sửa tay phần INSERT summary.")
    L.append("-- " + "=" * 75)
    L.append("")

    # ---------------- CREATE TABLE ----------------
    L.append("-- 1) ===== CREATE TABLE =====")
    L.append("""DROP TABLE IF EXISTS respondents;
CREATE TABLE respondents (
    respondent_id   INTEGER PRIMARY KEY,
    country         TEXT,
    employment      TEXT,
    dev_type        TEXT,
    years_code_pro  REAL,
    comp_total      REAL          -- thu nhập quy đổi USD/năm (ConvertedComp)
);

DROP TABLE IF EXISTS respondent_profile;
CREATE TABLE respondent_profile (
    respondent_id     INTEGER PRIMARY KEY,
    ed_level          TEXT,
    operating_system  TEXT,
    age               REAL,
    work_week_hrs     REAL,
    FOREIGN KEY (respondent_id) REFERENCES respondents(respondent_id)
);

-- Bảng FACT long-format: 1 dòng = 1 (respondent, skill, loại sử dụng).
-- Sinh bằng Python: explode các cột multi-select của clean_it_skills_data.csv.
DROP TABLE IF EXISTS skill_usage;
CREATE TABLE skill_usage (
    respondent_id  INTEGER,
    skill_category TEXT,         -- 'programming_language' | 'database' | 'ide' | ...
    skill_name     TEXT,
    usage_type     TEXT          -- 'worked_with' | 'desire_next_year'
);
CREATE INDEX IF NOT EXISTS idx_su_cat  ON skill_usage(skill_category);
CREATE INDEX IF NOT EXISTS idx_su_name ON skill_usage(skill_name);
CREATE INDEX IF NOT EXISTS idx_su_type ON skill_usage(usage_type);

-- Bảng TỔNG HỢP số liệu THẬT (đã tính từ toàn bộ 11.552 dòng) để truy vấn
-- phân tích trả về đúng xếp hạng ngay cả khi chỉ nạp dữ liệu mẫu ở trên.
DROP TABLE IF EXISTS skill_signal_summary;
CREATE TABLE skill_signal_summary (
    skill_category    TEXT,
    skill_name        TEXT,
    worked_with       INTEGER,
    desire_next_year  INTEGER,
    growth_gap        INTEGER,
    growth_pct        REAL,
    signal            TEXT,
    PRIMARY KEY (skill_category, skill_name)
);

DROP TABLE IF EXISTS salary_by_language;
CREATE TABLE salary_by_language (
    language        TEXT PRIMARY KEY,
    developer_count INTEGER,
    median_salary   REAL,
    mean_salary     REAL
);

DROP TABLE IF EXISTS role_priority;
CREATE TABLE role_priority (
    role                  TEXT PRIMARY KEY,
    developer_count       INTEGER,
    median_salary         REAL,
    hiring_priority_score REAL,
    priority_band         TEXT
);
""")

    # ---------------- INSERT demo skill_usage ----------------
    L.append("-- 2) ===== INSERT DỮ LIỆU MẪU (DEMO để chạy độc lập) =====")
    L.append("-- Trong pipeline thật: nạp clean_it_skills_data.csv rồi explode bằng Python,")
    L.append("-- hoặc dùng .import của SQLite. Dưới đây là vài respondent minh họa.")
    L.append("""INSERT INTO respondents VALUES
 (1,'Vietnam','Employed full-time','Full-stack developer',3,18000),
 (2,'United States','Employed full-time','Back-end developer',10,120000),
 (3,'India','Employed full-time','Data scientist or machine learning specialist',6,35000),
 (4,'Germany','Employed full-time','DevOps specialist',12,85000);

INSERT INTO skill_usage VALUES
 (1,'programming_language','Python','worked_with'),
 (1,'programming_language','JavaScript','worked_with'),
 (1,'programming_language','Rust','desire_next_year'),
 (1,'database','PostgreSQL','worked_with'),
 (1,'ide','Visual Studio Code','worked_with'),
 (2,'programming_language','Java','worked_with'),
 (2,'programming_language','Go','desire_next_year'),
 (2,'database','PostgreSQL','worked_with'),
 (2,'ide','IntelliJ','worked_with'),
 (3,'programming_language','Python','worked_with'),
 (3,'programming_language','TypeScript','desire_next_year'),
 (3,'database','MongoDB','desire_next_year'),
 (3,'ide','IPython / Jupyter','worked_with'),
 (4,'programming_language','Go','worked_with'),
 (4,'database','Redis','desire_next_year'),
 (4,'ide','Vim','worked_with');
""")

    # ---------------- INSERT real summary ----------------
    L.append("-- 3) ===== INSERT SỐ LIỆU THẬT (tổng hợp toàn bộ khảo sát) =====")
    rows = []
    for _, r in lang.iterrows():
        rows.append(f" ('programming_language','{esc(r['language'])}',{r['worked']},"
                    f"{r['desired_next_year']},{r['net_change']},{r['growth_pct']},'{r['signal']}')")
    for _, r in db.iterrows():
        rows.append(f" ('database','{esc(r['database'])}',{r['worked']},"
                    f"{r['desired_next_year']},{r['net_change']},{r['growth_pct']},'{r['signal']}')")
    L.append("INSERT INTO skill_signal_summary VALUES\n" + ",\n".join(rows) + ";")
    L.append("")
    # IDE summary -> dùng skill_signal_summary với category 'ide' (chỉ có worked)
    ide_rows = [f" ('ide','{esc(r['ide'])}',{r['developer_count']},NULL,NULL,NULL,'Stable')"
                for _, r in ide.iterrows()]
    L.append("INSERT INTO skill_signal_summary (skill_category,skill_name,worked_with,"
             "desire_next_year,growth_gap,growth_pct,signal) VALUES\n" + ",\n".join(ide_rows) + ";")
    L.append("")
    sal_rows = [f" ('{esc(r['language'])}',{r['developer_count']},{r['median_salary']},{r['mean_salary']})"
                for _, r in sal.iterrows()]
    L.append("INSERT INTO salary_by_language VALUES\n" + ",\n".join(sal_rows) + ";")
    L.append("")
    role_rows = [f" ('{esc(r['role'])}',{r['developer_count']},{r['median_salary']},"
                 f"{r['hiring_priority_score']},'{r['priority_band']}')"
                 for _, r in role.iterrows()]
    L.append("INSERT INTO role_priority VALUES\n" + ",\n".join(role_rows) + ";")
    L.append("")

    # ---------------- SELECT analytics ----------------
    L.append("-- 4) ===== SELECT — TRUY VẤN PHÂN TÍCH =====")
    L.append("""
-- (4.0) Cách chạy trên skill_usage THẬT: sau khi nạp đủ dữ liệu long-format,
--       các truy vấn 4.1-4.3 dưới đây cho ra xếp hạng thật. Với dữ liệu DEMO,
--       hãy dùng bảng skill_signal_summary (4.4+) để thấy số liệu thật.

-- (4.1) CÂU HỎI 1 — Top 10 ngôn ngữ ĐANG dùng (current).
SELECT skill_name, COUNT(*) AS total_users
FROM skill_usage
WHERE skill_category = 'programming_language' AND usage_type = 'worked_with'
GROUP BY skill_name ORDER BY total_users DESC LIMIT 10;

-- (4.2) Top 10 ngôn ngữ MUỐN dùng năm tới (desired).
SELECT skill_name, COUNT(*) AS total_users
FROM skill_usage
WHERE skill_category = 'programming_language' AND usage_type = 'desire_next_year'
GROUP BY skill_name ORDER BY total_users DESC LIMIT 10;

-- (4.3) EMERGING SKILL GAP trên long-format (desired - worked).
SELECT cur.skill_name,
       COALESCE(fut.future_count,0)  AS desired_count,
       COALESCE(cur.current_count,0) AS current_count,
       COALESCE(fut.future_count,0) - COALESCE(cur.current_count,0) AS growth_gap
FROM (SELECT skill_name, COUNT(*) current_count FROM skill_usage
      WHERE usage_type='worked_with' GROUP BY skill_name) cur
LEFT JOIN (SELECT skill_name, COUNT(*) future_count FROM skill_usage
           WHERE usage_type='desire_next_year' GROUP BY skill_name) fut
  ON cur.skill_name = fut.skill_name
ORDER BY growth_gap DESC;

-- ----- Truy vấn trên SỐ LIỆU THẬT (skill_signal_summary) -----

-- (4.4) CÂU HỎI 1 — Top ngôn ngữ theo nhu cầu năm tới (thật).
SELECT skill_name, worked_with, desire_next_year, growth_pct, signal
FROM skill_signal_summary
WHERE skill_category='programming_language'
ORDER BY desire_next_year DESC LIMIT 10;

-- (4.5) CÂU HỎI 2 — Database nổi bật nhất (thật).
SELECT skill_name, worked_with, desire_next_year, growth_pct, signal
FROM skill_signal_summary
WHERE skill_category='database'
ORDER BY desire_next_year DESC LIMIT 10;

-- (4.6) CÂU HỎI 3 — IDE / môi trường phát triển phổ biến nhất (thật).
SELECT skill_name, worked_with AS developer_count
FROM skill_signal_summary
WHERE skill_category='ide'
ORDER BY developer_count DESC LIMIT 10;

-- (4.7) CÂU HỎI 4 — Kỹ năng EMERGING (tăng trưởng mạnh, signal='Emerging').
SELECT skill_category, skill_name, worked_with, desire_next_year, growth_gap, growth_pct
FROM skill_signal_summary
WHERE signal='Emerging'
ORDER BY growth_pct DESC;

-- (4.8) Đối chiếu lương theo ngôn ngữ (giao tín hiệu tăng trưởng + lương).
SELECT s.skill_name, s.growth_pct, l.median_salary, l.developer_count
FROM skill_signal_summary s
JOIN salary_by_language l ON l.language = s.skill_name
WHERE s.skill_category='programming_language'
ORDER BY l.median_salary DESC;

-- (4.9) Ưu tiên tuyển dụng/đào tạo theo vai trò.
SELECT role, developer_count, median_salary, hiring_priority_score, priority_band
FROM role_priority ORDER BY hiring_priority_score DESC;

-- (4.10) SO SÁNH THEO QUỐC GIA (chạy trên dữ liệu thật khi đã nạp skill_usage
--        + respondents): top 5 ngôn ngữ mỗi quốc gia.
SELECT r.country, su.skill_name, COUNT(*) AS users
FROM skill_usage su JOIN respondents r ON r.respondent_id = su.respondent_id
WHERE su.skill_category='programming_language' AND su.usage_type='worked_with'
GROUP BY r.country, su.skill_name
ORDER BY r.country, users DESC;

-- (4.11) SO SÁNH THEO KINH NGHIỆM: nhóm theo years_code_pro, đếm kỹ năng.
SELECT CASE
         WHEN r.years_code_pro < 3  THEN '0-2 năm'
         WHEN r.years_code_pro < 6  THEN '3-5 năm'
         WHEN r.years_code_pro < 11 THEN '6-10 năm'
         ELSE '10+ năm' END AS exp_group,
       su.skill_name, COUNT(*) AS users
FROM skill_usage su JOIN respondents r ON r.respondent_id = su.respondent_id
WHERE su.skill_category='programming_language' AND su.usage_type='worked_with'
GROUP BY exp_group, su.skill_name
ORDER BY exp_group, users DESC;

-- (4.12) Tương quan đơn giản kinh nghiệm vs lương (Pearson r) — chạy trên
--        respondents thật. Đây là kỹ thuật thống kê thứ 3 (tùy chọn).
SELECT (COUNT(*)*SUM(years_code_pro*comp_total) - SUM(years_code_pro)*SUM(comp_total)) /
       ( SQRT(COUNT(*)*SUM(years_code_pro*years_code_pro) - SUM(years_code_pro)*SUM(years_code_pro)) *
         SQRT(COUNT(*)*SUM(comp_total*comp_total)   - SUM(comp_total)*SUM(comp_total)) )
       AS pearson_exp_vs_salary
FROM respondents
WHERE years_code_pro IS NOT NULL AND comp_total IS NOT NULL;
""")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[ok] -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
