-- =============================================================================
-- FINAL PROJECT - VTI ACADEMY
-- File   : queries.sql
-- Mục đích: Tạo bảng (CREATE TABLE), nạp dữ liệu mẫu (INSERT) và viết
--          các truy vấn phân tích (SELECT) trả lời cho 4 câu hỏi của dự án:
--            (1) Ngôn ngữ lập trình nào được yêu cầu nhiều nhất?
--            (2) Database nào được yêu cầu nhiều nhất?
--            (3) IDE phổ biến nhất là gì?
--            (4) Kỹ năng nào đang nổi (emerging) - so sánh Hiện tại vs Mong muốn?
-- Dialect: SQLite (tương thích MySQL/PostgreSQL với chỉnh nhỏ).
-- =============================================================================


-- =============================================================================
-- 1. CREATE TABLE
-- =============================================================================

-- 1.1 Bảng khảo sát Stack Overflow (chỉ những cột cần cho phân tích)
DROP TABLE IF EXISTS survey;
CREATE TABLE survey (
    respondent              INTEGER PRIMARY KEY,    -- Mã người trả lời
    country                 TEXT,                   -- Quốc gia
    employment              TEXT,                   -- Tình trạng việc làm
    ed_level                TEXT,                   -- Trình độ học vấn
    years_code              REAL,                   -- Số năm code
    years_code_pro          REAL,                   -- Số năm code chuyên nghiệp
    age                     REAL,                   -- Tuổi
    language_worked_with    TEXT,                   -- Ngôn ngữ đang dùng
    language_desire_next_year TEXT,                 -- Ngôn ngữ muốn dùng
    database_worked_with    TEXT,                   -- Database đang dùng
    database_desire_next_year TEXT,                 -- Database muốn dùng
    dev_environ             TEXT                    -- IDE đang dùng
);

-- 1.2 Bảng tin tuyển dụng ItViec
DROP TABLE IF EXISTS itviec_jobs;
CREATE TABLE itviec_jobs (
    job_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title       TEXT NOT NULL,
    company         TEXT,
    location        TEXT,
    salary          TEXT,
    salary_min_usd  REAL,
    salary_max_usd  REAL,
    skills          TEXT,                          -- Skill nối nhau bằng ';'
    source_url      TEXT,
    source          TEXT DEFAULT 'ItViec'
);

-- 1.3 Bảng FACT long-format - mỗi dòng = 1 lượt skill xuất hiện
-- Đây là bảng chính ghép từ cả 2 nguồn để phân tích chéo.
DROP TABLE IF EXISTS skill_report;
CREATE TABLE skill_report (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,                 -- 'StackOverflow' | 'ItViec'
    country         TEXT,
    skill_type      TEXT,                          -- language|database|ide|...
    skill_name      TEXT NOT NULL,
    job_title       TEXT,                          -- Có khi source = ItViec
    company         TEXT,
    respondent_id   INTEGER                        -- Có khi source = StackOverflow
);

-- 1.4 Bảng summary đã pivot - tổng lượt theo skill, chia theo nguồn
DROP TABLE IF EXISTS skill_summary;
CREATE TABLE skill_summary (
    skill_name      TEXT PRIMARY KEY,
    StackOverflow   INTEGER DEFAULT 0,
    ItViec          INTEGER DEFAULT 0,
    total           INTEGER DEFAULT 0
);

-- Tạo index để tăng tốc truy vấn theo skill_name / skill_type
CREATE INDEX IF NOT EXISTS idx_report_skill_name ON skill_report(skill_name);
CREATE INDEX IF NOT EXISTS idx_report_skill_type ON skill_report(skill_type);
CREATE INDEX IF NOT EXISTS idx_report_source     ON skill_report(source);


-- =============================================================================
-- 2. INSERT - DỮ LIỆU MẪU (DEMO)
-- =============================================================================
-- Trong pipeline thật, dữ liệu được Python nạp tự động qua pandas.to_sql().
-- Phần INSERT dưới đây là dữ liệu mẫu để có thể chạy thử SQL độc lập.

-- 2.1 Survey
INSERT INTO survey (respondent, country, employment, ed_level, years_code,
                    years_code_pro, age, language_worked_with,
                    language_desire_next_year, database_worked_with,
                    database_desire_next_year, dev_environ) VALUES
(1, 'Vietnam',       'Employed full-time', 'Bachelor', 5,  3, 26,
    'Python;JavaScript;SQL', 'Python;Go;Rust',
    'MySQL;PostgreSQL',      'PostgreSQL;MongoDB',
    'VS Code;PyCharm'),
(2, 'United States', 'Employed full-time', 'Master',   12, 10, 35,
    'Java;Kotlin;SQL',       'Kotlin;Go',
    'PostgreSQL;Oracle',     'PostgreSQL;Redis',
    'IntelliJ;VS Code'),
(3, 'India',         'Employed full-time', 'Bachelor', 8,  6, 29,
    'JavaScript;TypeScript;Python', 'TypeScript;Rust',
    'MongoDB;Redis',         'MongoDB;PostgreSQL',
    'VS Code;WebStorm'),
(4, 'Vietnam',       'Student',            'Bachelor', 2,  0, 21,
    'Python;C++',            'Python;Rust',
    'MySQL',                 'PostgreSQL',
    'VS Code'),
(5, 'Germany',       'Employed full-time', 'Master',   15, 12, 38,
    'C#;TypeScript;SQL',     'Go;TypeScript',
    'SQL Server;PostgreSQL', 'PostgreSQL',
    'Visual Studio;VS Code');

-- 2.2 ItViec jobs
INSERT INTO itviec_jobs (job_title, company, location, salary,
                         salary_min_usd, salary_max_usd, skills, source_url) VALUES
('Senior Python Developer',     'FPT Software', 'Ho Chi Minh', '1500-2500 USD',
 1500, 2500, 'Python;Django;PostgreSQL;Docker', 'https://itviec.com/job/1'),
('Java Backend Engineer',       'VNG',          'Ho Chi Minh', '1200-2000 USD',
 1200, 2000, 'Java;Spring Boot;MySQL;Kafka',    'https://itviec.com/job/2'),
('Frontend ReactJS Developer',  'Tiki',         'Ho Chi Minh', '1000-1800 USD',
 1000, 1800, 'JavaScript;React;TypeScript;Node.js', 'https://itviec.com/job/3'),
('Data Engineer',               'Shopee',       'Ha Noi',      '1800-3000 USD',
 1800, 3000, 'Python;SQL;Spark;AWS',            'https://itviec.com/job/4'),
('.NET Developer',              'TMA Solutions','Ho Chi Minh', '900-1500 USD',
 900,  1500, 'C#;.NET;SQL Server;Azure',        'https://itviec.com/job/5');

-- 2.3 Skill report (long-format) - lấy từ kết quả explode trên
INSERT INTO skill_report (source, country, skill_type, skill_name,
                          job_title, company, respondent_id) VALUES
('StackOverflow','Vietnam','language','Python',       NULL, NULL, 1),
('StackOverflow','Vietnam','language','JavaScript',   NULL, NULL, 1),
('StackOverflow','Vietnam','language','SQL',          NULL, NULL, 1),
('StackOverflow','Vietnam','database','MySQL',        NULL, NULL, 1),
('StackOverflow','Vietnam','ide',     'VS Code',      NULL, NULL, 1),
('ItViec','Vietnam','job_requirement','Python',       'Senior Python Developer',    'FPT Software', NULL),
('ItViec','Vietnam','job_requirement','Django',       'Senior Python Developer',    'FPT Software', NULL),
('ItViec','Vietnam','job_requirement','PostgreSQL',   'Senior Python Developer',    'FPT Software', NULL),
('ItViec','Vietnam','job_requirement','Java',         'Java Backend Engineer',      'VNG',          NULL),
('ItViec','Vietnam','job_requirement','Spring Boot',  'Java Backend Engineer',      'VNG',          NULL),
('ItViec','Vietnam','job_requirement','React',        'Frontend ReactJS Developer', 'Tiki',         NULL),
('ItViec','Vietnam','job_requirement','TypeScript',   'Frontend ReactJS Developer', 'Tiki',         NULL);


-- =============================================================================
-- 3. SELECT - TRUY VẤN PHÂN TÍCH
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 3.1 CÂU HỎI 1: Ngôn ngữ lập trình nào đang được yêu cầu NHIỀU NHẤT?
-- -----------------------------------------------------------------------------
-- Logic: Lọc skill_type = 'language' (từ khảo sát) hoặc skill có trong JD ItViec,
--        gom nhóm theo skill_name, đếm lượt xuất hiện.
SELECT
    skill_name        AS language,
    COUNT(*)          AS total_mentions,
    SUM(CASE WHEN source = 'StackOverflow' THEN 1 ELSE 0 END) AS from_survey,
    SUM(CASE WHEN source = 'ItViec'        THEN 1 ELSE 0 END) AS from_jobs
FROM skill_report
WHERE skill_type IN ('language', 'job_requirement')
GROUP BY skill_name
ORDER BY total_mentions DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 3.2 CÂU HỎI 2: Database nào đang được yêu cầu NHIỀU NHẤT?
-- -----------------------------------------------------------------------------
-- Lưu ý: Trong JD ItViec, database cũng được gắn skill_type='job_requirement',
--        nên ta nhận diện bằng cách so khớp với danh sách database phổ biến.
SELECT
    skill_name        AS database_name,
    COUNT(*)          AS total_mentions
FROM skill_report
WHERE skill_name IN (
    'MySQL','PostgreSQL','MongoDB','Redis','Oracle','SQL Server',
    'SQLite','Cassandra','DynamoDB','Elasticsearch','MariaDB'
)
GROUP BY skill_name
ORDER BY total_mentions DESC;


-- -----------------------------------------------------------------------------
-- 3.3 CÂU HỎI 3: IDE phổ biến nhất là gì?
-- -----------------------------------------------------------------------------
-- IDE chỉ có trong khảo sát Stack Overflow (cột dev_environ).
SELECT
    skill_name        AS ide,
    COUNT(*)          AS users
FROM skill_report
WHERE skill_type = 'ide'
GROUP BY skill_name
ORDER BY users DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 3.4 CÂU HỎI 4: Kỹ năng nào đang "NỔI" (emerging)?
-- -----------------------------------------------------------------------------
-- Định nghĩa: kỹ năng được mention nhiều ở JD (ItViec) nhưng còn ít trong
-- khảo sát Stack Overflow (cộng đồng dev hiện chưa rành) -> nhu cầu lớn,
-- cung còn thấp -> emerging.
SELECT
    skill_name,
    SUM(CASE WHEN source = 'ItViec'        THEN 1 ELSE 0 END) AS demand_jobs,
    SUM(CASE WHEN source = 'StackOverflow' THEN 1 ELSE 0 END) AS supply_devs,
    ROUND(
        1.0 * SUM(CASE WHEN source = 'ItViec' THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN source = 'StackOverflow' THEN 1 ELSE 0 END), 0),
        2
    ) AS demand_supply_ratio
FROM skill_report
GROUP BY skill_name
HAVING demand_jobs >= 1
ORDER BY demand_supply_ratio DESC NULLS LAST, demand_jobs DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- 3.5 PHÂN PHỐI THEO QUỐC GIA (top 5 ngôn ngữ ở mỗi quốc gia)
-- -----------------------------------------------------------------------------
WITH lang_country AS (
    SELECT country, skill_name, COUNT(*) AS cnt
    FROM skill_report
    WHERE skill_type = 'language'
    GROUP BY country, skill_name
),
ranked AS (
    SELECT
        country, skill_name, cnt,
        ROW_NUMBER() OVER (PARTITION BY country ORDER BY cnt DESC) AS rk
    FROM lang_country
)
SELECT country, skill_name, cnt
FROM ranked
WHERE rk <= 5
ORDER BY country, rk;


-- -----------------------------------------------------------------------------
-- 3.6 PHÂN TÍCH LƯƠNG ĐỐI VỚI TỪNG KỸ NĂNG (ItViec)
-- -----------------------------------------------------------------------------
-- Mức lương trung bình cho từng skill bằng cách JOIN itviec_jobs với
-- skill_report (vì JD đã được explode thành từng skill).
SELECT
    sr.skill_name,
    COUNT(DISTINCT ij.job_id)            AS num_jobs,
    ROUND(AVG(ij.salary_min_usd), 0)     AS avg_min_usd,
    ROUND(AVG(ij.salary_max_usd), 0)     AS avg_max_usd
FROM skill_report sr
JOIN itviec_jobs ij
  ON sr.job_title = ij.job_title
 AND sr.company   = ij.company
WHERE sr.source = 'ItViec'
GROUP BY sr.skill_name
HAVING num_jobs >= 1
ORDER BY avg_max_usd DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 3.7 SO SÁNH "ĐANG DÙNG" vs "MUỐN DÙNG" NĂM SAU (Stack Overflow)
-- -----------------------------------------------------------------------------
-- Trả lời: ngôn ngữ nào đang dùng nhiều nhưng ít người muốn tiếp tục?
-- Logic: split chuỗi ngăn cách bởi ';' bằng recursive CTE (SQLite hỗ trợ).
WITH RECURSIVE split_now(respondent, lang, rest) AS (
    SELECT respondent, '', language_worked_with || ';'
    FROM survey
    UNION ALL
    SELECT
        respondent,
        substr(rest, 0, instr(rest, ';')),
        substr(rest, instr(rest, ';') + 1)
    FROM split_now
    WHERE rest != ''
),
now_counts AS (
    SELECT lang AS skill_name, COUNT(*) AS now_count
    FROM split_now WHERE lang != '' GROUP BY lang
),
split_next(respondent, lang, rest) AS (
    SELECT respondent, '', language_desire_next_year || ';'
    FROM survey
    UNION ALL
    SELECT
        respondent,
        substr(rest, 0, instr(rest, ';')),
        substr(rest, instr(rest, ';') + 1)
    FROM split_next
    WHERE rest != ''
),
next_counts AS (
    SELECT lang AS skill_name, COUNT(*) AS next_count
    FROM split_next WHERE lang != '' GROUP BY lang
)
SELECT
    COALESCE(n.skill_name, x.skill_name)            AS language,
    COALESCE(n.now_count, 0)                        AS using_now,
    COALESCE(x.next_count, 0)                       AS desired_next_year,
    COALESCE(x.next_count, 0) - COALESCE(n.now_count, 0) AS delta
FROM now_counts n
FULL OUTER JOIN next_counts x ON n.skill_name = x.skill_name
ORDER BY delta DESC;


-- -----------------------------------------------------------------------------
-- 3.8 BẢNG SUMMARY DASHBOARD (TOP 10 KỸ NĂNG, KÈM TỶ TRỌNG TỪNG NGUỒN)
-- -----------------------------------------------------------------------------
-- Dùng làm bảng đầu vào trực tiếp cho Power BI (Bar chart).
SELECT
    skill_name,
    SUM(CASE WHEN source = 'StackOverflow' THEN 1 ELSE 0 END) AS so_count,
    SUM(CASE WHEN source = 'ItViec'        THEN 1 ELSE 0 END) AS itviec_count,
    COUNT(*)                                                  AS total,
    ROUND(100.0 * SUM(CASE WHEN source = 'ItViec' THEN 1 ELSE 0 END)
                  / COUNT(*), 1)                              AS pct_from_itviec
FROM skill_report
GROUP BY skill_name
ORDER BY total DESC
LIMIT 10;
