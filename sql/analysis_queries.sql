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
 ('programming_language','Python',18410,12419,-5991,-32.5,'Declining'),
 ('programming_language','SQL',18633,11257,-7376,-39.6,'Declining'),
 ('programming_language','HTML/CSS',19698,10661,-9037,-45.9,'Declining'),
 ('programming_language','JavaScript',21005,10581,-10424,-49.6,'Declining'),
 ('programming_language','TypeScript',13859,10099,-3760,-27.1,'Declining'),
 ('programming_language','Rust',4724,9262,4538,96.1,'Emerging'),
 ('programming_language','Bash/Shell (all shells)',15503,8662,-6841,-44.1,'Declining'),
 ('programming_language','Go',5219,7414,2195,42.1,'Emerging'),
 ('programming_language','C#',8852,6117,-2735,-30.9,'Declining'),
 ('programming_language','C++',7485,5243,-2242,-30.0,'Declining'),
 ('programming_language','Java',9358,4981,-4377,-46.8,'Declining'),
 ('programming_language','C',6987,4548,-2439,-34.9,'Declining'),
 ('programming_language','Kotlin',3420,3786,366,10.7,'Stable'),
 ('programming_language','PowerShell',7371,3014,-4357,-59.1,'Declining'),
 ('programming_language','PHP',5994,2873,-3121,-52.1,'Declining'),
 ('programming_language','Zig',680,2415,1735,255.1,'Emerging'),
 ('programming_language','Lua',2910,2389,-521,-17.9,'Stable'),
 ('programming_language','Assembly',2246,2154,-92,-4.1,'Stable'),
 ('programming_language','Swift',1719,2033,314,18.3,'Stable'),
 ('programming_language','Elixir',847,1818,971,114.6,'Emerging'),
 ('programming_language','Dart',1885,1653,-232,-12.3,'Stable'),
 ('programming_language','Ruby',2046,1587,-459,-22.4,'Declining'),
 ('programming_language','R',1569,1308,-261,-16.6,'Stable'),
 ('programming_language','Lisp',753,1136,383,50.9,'Emerging'),
 ('programming_language','GDScript',1062,1072,10,0.9,'Stable'),
 ('programming_language','Gleam',354,972,618,174.6,'Emerging'),
 ('programming_language','Erlang',465,956,491,105.6,'Emerging'),
 ('programming_language','Scala',843,924,81,9.6,'Stable'),
 ('programming_language','F#',406,908,502,123.6,'Emerging'),
 ('programming_language','OCaml',367,864,497,135.4,'Emerging'),
 ('programming_language','MicroPython',723,831,108,14.9,'Stable'),
 ('programming_language','Perl',1215,701,-514,-42.3,'Declining'),
 ('programming_language','MATLAB',1231,617,-614,-49.9,'Declining'),
 ('programming_language','Groovy',1535,606,-929,-60.5,'Declining'),
 ('programming_language','Visual Basic (.Net)',1409,577,-832,-59.0,'Declining'),
 ('programming_language','Mojo',145,572,427,294.5,'Emerging'),
 ('programming_language','Delphi',796,563,-233,-29.3,'Declining'),
 ('programming_language','Ada',431,511,80,18.6,'Stable'),
 ('programming_language','VBA',1334,481,-853,-63.9,'Declining'),
 ('programming_language','Prolog',338,414,76,22.5,'Emerging'),
 ('programming_language','COBOL',308,403,95,30.8,'Emerging'),
 ('programming_language','Fortran',449,397,-52,-11.6,'Stable'),
 ('database','PostgreSQL',14529,11863,-2666,-18.3,'Stable'),
 ('database','SQLite',9798,7185,-2613,-26.7,'Declining'),
 ('database','Redis',7316,6014,-1302,-17.8,'Stable'),
 ('database','MySQL',10581,5120,-5461,-51.6,'Declining'),
 ('database','MongoDB',6267,4421,-1846,-29.5,'Declining'),
 ('database','Microsoft SQL Server',7871,3851,-4020,-51.1,'Declining'),
 ('database','Elasticsearch',4347,3288,-1059,-24.4,'Declining'),
 ('database','MariaDB',5862,3239,-2623,-44.7,'Declining'),
 ('database','Dynamodb',2551,1741,-810,-31.8,'Declining'),
 ('database','Supabase',1558,1621,63,4.0,'Stable'),
 ('database','DuckDB',863,1436,573,66.4,'Emerging'),
 ('database','BigQuery',1705,1371,-334,-19.6,'Stable'),
 ('database','Oracle',2761,1259,-1502,-54.4,'Declining'),
 ('database','Valkey',632,1240,608,96.2,'Emerging'),
 ('database','Cassandra',766,1214,448,58.5,'Emerging'),
 ('database','Snowflake',1079,1068,-11,-1.0,'Stable'),
 ('database','Firebase Realtime Database',1299,1010,-289,-22.2,'Declining'),
 ('database','Cosmos DB',1190,988,-202,-17.0,'Stable'),
 ('database','Cloud Firestore',1494,980,-514,-34.4,'Declining'),
 ('database','Neo4J',691,972,281,40.7,'Emerging'),
 ('database','Databricks SQL',895,874,-21,-2.3,'Stable'),
 ('database','Clickhouse',627,844,217,34.6,'Emerging'),
 ('database','InfluxDB',963,721,-242,-25.1,'Declining'),
 ('database','Amazon Redshift',611,685,74,12.1,'Stable'),
 ('database','Cockroachdb',262,632,370,141.2,'Emerging'),
 ('database','H2',1303,620,-683,-52.4,'Declining'),
 ('database','Pocketbase',262,407,145,55.3,'Emerging'),
 ('database','Microsoft Access',1244,363,-881,-70.8,'Declining'),
 ('database','IBM DB2',615,330,-285,-46.3,'Declining'),
 ('database','Datomic',148,272,124,83.8,'Emerging');

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
 ('Ruby',1550,102961,114831),
 ('Erlang',314,100000,108905),
 ('Perl',806,99886,112073),
 ('Elixir',615,99194,109543),
 ('Scala',600,96524,114361),
 ('Swift',1198,92000,104009),
 ('Groovy',1171,90233,101916),
 ('Lisp',459,90000,107780),
 ('Go',3783,89815,105716),
 ('Bash/Shell (all shells)',11104,83531,97342),
 ('Rust',3117,83000,101345),
 ('Zig',399,81210,96562),
 ('PowerShell',5334,80992,89809),
 ('Kotlin',2428,80152,93572),
 ('F#',262,80127,91521),
 ('TypeScript',10336,79648,92141),
 ('C#',6397,78616,89654),
 ('Gleam',209,77730,90917),
 ('Python',12730,76828,92689),
 ('SQL',13546,76518,90007),
 ('JavaScript',14873,75410,88540),
 ('OCaml',199,75410,99022),
 ('Lua',1857,75320,92640),
 ('Java',6283,75109,89963),
 ('C++',4605,74249,90234),
 ('HTML/CSS',13782,74000,86575),
 ('Fortran',271,73516,87466),
 ('C',4095,72958,88707),
 ('VBA',908,71814,85025),
 ('MicroPython',408,70705,87409),
 ('R',1011,70000,86542),
 ('Assembly',1187,69609,86517),
 ('GDScript',622,68036,84956),
 ('Delphi',471,67655,73985),
 ('Visual Basic (.Net)',966,65462,74567),
 ('PHP',4097,60000,72099),
 ('MATLAB',700,58007,75035),
 ('COBOL',182,58007,75772),
 ('Dart',1201,50000,70558),
 ('Prolog',172,49886,80150),
 ('Ada',216,44245,65346);

INSERT INTO role_priority VALUES
 ('Full-stack Developer',12351,71078.0,77.2,'Priority 1'),
 ('Back-end Developer',6453,78616.0,46.1,'Priority 2'),
 ('Product/BA',1273,122171.0,35.4,'Priority 3'),
 ('DevOps Specialist',1053,87011.0,18.4,'Priority 3'),
 ('Data Scientist / ML',574,81210.0,13.0,'Priority 3'),
 ('Mobile Developer',1391,69609.0,12.6,'Priority 3'),
 ('Front-end Developer',1974,61362.0,12.3,'Priority 3'),
 ('Data/BI Analyst',351,55000.0,0.0,'Priority 3');

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

