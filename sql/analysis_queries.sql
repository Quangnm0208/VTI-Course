-- ===========================================================================
-- VTI ACADEMY — FINAL PROJECT | analysis_queries.sql
-- Phân tích kỹ năng IT từ khảo sát Stack Overflow (11.552 dev / 135 nước).
-- Cấu trúc long-format 'skill_usage' + bảng tổng hợp số liệu THẬT.
-- Dialect: SQLite. (MySQL: bỏ 'IF NOT EXISTS' cho INDEX; PostgreSQL: ok.)
-- File này được sinh bởi analysis/build_sql.py để số liệu luôn khớp
-- dashboard, notebook và slide. KHÔNG sửa tay phần INSERT summary.
-- ===========================================================================

-- 1) ===== CREATE TABLE =====
DROP TABLE IF EXISTS respondents;
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

-- 2) ===== INSERT DỮ LIỆU MẪU (DEMO để chạy độc lập) =====
-- Trong pipeline thật: nạp clean_it_skills_data.csv rồi explode bằng Python,
-- hoặc dùng .import của SQLite. Dưới đây là vài respondent minh họa.
INSERT INTO respondents VALUES
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

-- 3) ===== INSERT SỐ LIỆU THẬT (tổng hợp toàn bộ khảo sát) =====
INSERT INTO skill_signal_summary VALUES
 ('programming_language','JavaScript',8805,6715,-2090,-23.7,'Declining'),
 ('programming_language','HTML/CSS',7920,5398,-2522,-31.8,'Declining'),
 ('programming_language','Python',4611,5309,698,15.1,'Stable'),
 ('programming_language','SQL',7213,5094,-2119,-29.4,'Declining'),
 ('programming_language','TypeScript',3269,4140,871,26.6,'Emerging'),
 ('programming_language','C#',4346,3639,-707,-16.3,'Stable'),
 ('programming_language','Bash/Shell/PowerShell',4694,3135,-1559,-33.2,'Declining'),
 ('programming_language','Java',4556,2987,-1569,-34.4,'Declining'),
 ('programming_language','Go',1133,2813,1680,148.3,'Emerging'),
 ('programming_language','Kotlin',754,1907,1153,152.9,'Emerging'),
 ('programming_language','C++',1964,1645,-319,-16.2,'Stable'),
 ('programming_language','Rust',328,1540,1212,369.5,'Emerging'),
 ('programming_language','PHP',2950,1475,-1475,-50.0,'Declining'),
 ('programming_language','WebAssembly',136,1417,1281,941.9,'Emerging'),
 ('programming_language','C',1601,1040,-561,-35.0,'Declining'),
 ('database','PostgreSQL',4153,4386,233,5.6,'Stable'),
 ('database','MongoDB',3058,3703,645,21.1,'Emerging'),
 ('database','Redis',2536,3385,849,33.5,'Emerging'),
 ('database','MySQL',5549,3328,-2221,-40.0,'Declining'),
 ('database','Elasticsearch',1980,2898,918,46.4,'Emerging'),
 ('database','Microsoft SQL Server',4170,2747,-1423,-34.1,'Declining'),
 ('database','SQLite',3292,2465,-827,-25.1,'Declining'),
 ('database','Firebase',1343,1679,336,25.0,'Emerging'),
 ('database','MariaDB',1724,1400,-324,-18.8,'Stable'),
 ('database','DynamoDB',839,1056,217,25.9,'Emerging'),
 ('database','Cassandra',403,1023,620,153.8,'Emerging'),
 ('database','Oracle',1761,881,-880,-50.0,'Declining');

INSERT INTO skill_signal_summary (skill_category,skill_name,worked_with,desire_next_year,growth_gap,growth_pct,signal) VALUES
 ('ide','Visual Studio Code',8559,NULL,NULL,NULL,'Stable'),
 ('ide','Visual Studio',4732,NULL,NULL,NULL,'Stable'),
 ('ide','Notepad++',4642,NULL,NULL,NULL,'Stable'),
 ('ide','IntelliJ',3957,NULL,NULL,NULL,'Stable'),
 ('ide','Vim',3382,NULL,NULL,NULL,'Stable'),
 ('ide','Android Studio',2314,NULL,NULL,NULL,'Stable'),
 ('ide','PyCharm',2237,NULL,NULL,NULL,'Stable'),
 ('ide','Sublime Text',2201,NULL,NULL,NULL,'Stable'),
 ('ide','IPython / Jupyter',2010,NULL,NULL,NULL,'Stable'),
 ('ide','Eclipse',1789,NULL,NULL,NULL,'Stable');

INSERT INTO salary_by_language VALUES
 ('Clojure',152,93404,114203),
 ('Go',1060,80000,98923),
 ('Scala',461,79163,98884),
 ('Ruby',1094,75000,94376),
 ('Elixir',169,71966,89015),
 ('Rust',311,70000,88382),
 ('Bash/Shell/PowerShell',4417,68745,89946),
 ('Objective-C',483,64115,87429),
 ('Python',4293,64000,85750),
 ('R',552,63016,85477),
 ('Swift',668,60674,81501),
 ('TypeScript',3012,60173,80456),
 ('C#',3993,59112,79957),
 ('JavaScript',8136,58000,79063),
 ('SQL',6687,58284,78852),
 ('Java',4168,53437,75838),
 ('PHP',2720,43296,66879);

INSERT INTO role_priority VALUES
 ('Full-stack Developer',6928,59000,72.9,'Priority 1'),
 ('Back-end Developer',6290,56715,65.9,'Priority 2'),
 ('DevOps Specialist',1639,71036,46.1,'Priority 2'),
 ('Front-end Developer',3920,53437,45.2,'Priority 2'),
 ('Product/BA',1179,61650,33.3,'Priority 3'),
 ('Data/BI Analyst',802,61872,30.8,'Priority 3'),
 ('Data Scientist / ML',803,60000,28.9,'Priority 3'),
 ('Mobile Developer',1959,46152,23.5,'Priority 3');

-- 4) ===== SELECT — TRUY VẤN PHÂN TÍCH =====

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

