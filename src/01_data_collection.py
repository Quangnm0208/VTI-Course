"""
===============================================================================
 FINAL PROJECT - VTI ACADEMY
 File:    01_data_collection.py
 Mục đích: Thu thập dữ liệu từ 2 nguồn:
            1) Web Scraping tin tuyển dụng IT từ ItViec (https://itviec.com)
            2) File khảo sát Stack Overflow (Final Project.csv) - được copy
               sang thư mục data/raw để pipeline downstream sử dụng.
 Công cụ : requests, BeautifulSoup, pandas
 Tác giả : Data Analyst - VTI Academy
===============================================================================
"""

# -----------------------------------------------------------------------------
# 1. IMPORT THƯ VIỆN
# -----------------------------------------------------------------------------
import os                          # Thao tác file/đường dẫn
import re                          # Regex để bóc tách kỹ năng từ text
import time                        # Tạm dừng giữa các request (lịch sự)
import shutil                      # Copy file Excel/CSV về data/raw
import logging                     # Ghi log quá trình thu thập
import requests                    # Gửi HTTP request
import pandas as pd                # Xử lý DataFrame
from bs4 import BeautifulSoup      # Parse HTML
from typing import List, Dict, Optional

# -----------------------------------------------------------------------------
# 2. CẤU HÌNH CHUNG
# -----------------------------------------------------------------------------
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Header giả lập trình duyệt: ItViec sẽ trả về 403 nếu thiếu User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi,en;q=0.9",
}

# Cấu hình ItViec
ITVIEC_BASE  = "https://itviec.com"
ITVIEC_JOBS  = "https://itviec.com/it-jobs"
REQUEST_DELAY = 2.0                  # Nghỉ 2s giữa các trang để tránh bị chặn

# Từ điển kỹ năng IT phổ biến - dùng nhận diện skill từ tiêu đề/mô tả
SKILL_DICTIONARY = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "C",
    "Go", "Golang", "Ruby", "PHP", "Kotlin", "Swift", "Scala", "Rust",
    "Dart", "Objective-C", "R", "Perl", "Matlab", "VB.NET", "SQL",
    # Frameworks / Libraries
    "React", "ReactJS", "Angular", "Vue", "VueJS", "Next.js", "Nuxt",
    "Node.js", "NodeJS", "Express", "Django", "Flask", "FastAPI",
    "Spring", "Spring Boot", "Laravel", ".NET", "ASP.NET", "Rails",
    "Flutter", "React Native", "Xamarin", "Symfony", "CodeIgniter",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server",
    "SQLite", "Cassandra", "DynamoDB", "Elasticsearch", "MariaDB",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "Jenkins", "Git", "GitLab", "Terraform", "Ansible", "CI/CD",
    # Data / BI
    "Power BI", "Tableau", "Pandas", "NumPy", "TensorFlow", "PyTorch",
    "Spark", "Hadoop", "Airflow", "ETL", "Kafka",
    # OS
    "Linux", "Unix", "Windows Server",
]


# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)


# =============================================================================
# 3. WEB SCRAPING: ITVIEC
# =============================================================================
def fetch_page(url: str) -> Optional[str]:
    """
    Gửi GET request tới 1 URL, trả về HTML text (None nếu lỗi).
    Có timeout 30s và xử lý exception để pipeline không crash giữa chừng.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()                # Báo lỗi nếu status code != 2xx
        return resp.text
    except requests.RequestException as err:
        log.error("Lỗi khi tải %s: %s", url, err)
        return None


def extract_skills(text: str) -> str:
    """
    Bóc tách các kỹ năng IT trong 1 đoạn text dựa trên SKILL_DICTIONARY.
    Trả về chuỗi các kỹ năng nối bằng ";" (dễ explode khi wrangling).
    """
    if not text:
        return ""
    found = set()
    text_lower = text.lower()
    for skill in SKILL_DICTIONARY:
        # Dùng regex word-boundary để không bắt nhầm "Java" trong "JavaScript"
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)
    return ";".join(sorted(found))


def parse_job_card(card) -> Dict:
    """
    Bóc thông tin từ 1 thẻ HTML chứa 1 tin tuyển dụng ItViec.

    ItViec cấu trúc mỗi job nằm trong <div class="ipy-3"> hoặc tương tự,
    bên trong có:
        - <h3>: tên job
        - <a class="company-name">: công ty
        - <span class="address">: địa điểm
        - các <span class="itag"> chứa các skill tag
    """
    # Tên job
    title_tag = card.find(["h3", "h2"])
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Công ty - thử nhiều selector vì ItViec đôi khi đổi cấu trúc HTML
    company_tag = (
        card.find("a", class_=re.compile("company"))
        or card.find("span", class_=re.compile("company"))
        or card.find(class_=re.compile("employer"))
    )
    company = company_tag.get_text(strip=True) if company_tag else ""

    # Địa điểm
    loc_tag = card.find(class_=re.compile(r"(address|location|city)"))
    location = loc_tag.get_text(strip=True) if loc_tag else ""

    # Mức lương (ItViec hay ẩn cho công ty lớn -> "Login to view salary")
    salary_tag = card.find(class_=re.compile("salary"))
    salary = salary_tag.get_text(strip=True) if salary_tag else "Negotiable"

    # Tags kỹ năng - ItViec dùng class "itag" hoặc "tag"
    tag_nodes = card.find_all(class_=re.compile(r"(itag|tag|skill)"))
    tags = [t.get_text(strip=True) for t in tag_nodes if t.get_text(strip=True)]

    # Link chi tiết
    link_tag = card.find("a", href=True)
    detail_url = ""
    if link_tag:
        href = link_tag["href"]
        detail_url = href if href.startswith("http") else ITVIEC_BASE + href

    # Hợp nhất skill từ tags + skill bóc trong title
    combined_text = f"{title} {' '.join(tags)}"
    skills = extract_skills(combined_text)
    # Nếu có tags trực tiếp từ HTML thì ưu tiên dùng (chuẩn xác hơn parse text)
    if tags:
        skills = ";".join(sorted({t.strip() for t in tags if t.strip()}))

    return {
        "job_title":   title,
        "company":     company,
        "location":    location,
        "salary":      salary,
        "skills":      skills,
        "source_url":  detail_url,
        "source":      "ItViec",
    }


def scrape_itviec(max_pages: int = 50) -> pd.DataFrame:
    """
    Cào (scrape) toàn bộ tin tuyển dụng IT từ ItViec.

    Quy trình:
        B1: Lặp qua các trang ?page=1..N
        B2: Mỗi trang -> tải HTML -> parse bằng BeautifulSoup
        B3: Tìm các thẻ job-card -> bóc thông tin
        B4: Tích lũy vào list, dừng khi gặp trang không có job hoặc đủ N trang

    Args:
        max_pages: Số trang tối đa cần cào (mỗi trang ~20 jobs).

    Returns:
        DataFrame chứa các cột: job_title, company, location, salary,
        skills, source_url, source.
    """
    log.info("=== Bắt đầu scrape ItViec (tối đa %d trang) ===", max_pages)

    all_jobs: List[Dict] = []

    for page in range(1, max_pages + 1):
        url = f"{ITVIEC_JOBS}?page={page}"
        log.info("Đang tải trang %d: %s", page, url)

        html = fetch_page(url)
        if not html:
            log.warning("Bỏ qua trang %d do lỗi tải.", page)
            continue

        soup = BeautifulSoup(html, "html.parser")

        # ItViec có nhiều phiên bản layout - thử lần lượt các selector phổ biến
        job_cards = (
            soup.find_all("div", class_=re.compile(r"job.?card|ipy-3"))
            or soup.find_all("section", class_=re.compile("job"))
            or soup.find_all("article")
        )

        if not job_cards:
            log.info("Không tìm thấy job card ở trang %d -> dừng.", page)
            break

        log.info("Trang %d có %d job card", page, len(job_cards))

        for card in job_cards:
            try:
                job = parse_job_card(card)
                # Chỉ giữ job có ít nhất title (loại bỏ card rác)
                if job["job_title"]:
                    all_jobs.append(job)
            except Exception as err:
                # Không để 1 card lỗi làm crash cả pipeline
                log.warning("Lỗi parse card: %s", err)

        # Nghỉ trước khi sang trang kế tiếp - tránh bị block IP
        time.sleep(REQUEST_DELAY)

    df = pd.DataFrame(all_jobs)
    log.info("=== Scrape ItViec xong: %d bản ghi ===", len(df))
    return df


# =============================================================================
# 4. NẠP FILE EXCEL/CSV KHẢO SÁT (FINAL PROJECT.CSV)
# =============================================================================
def stage_survey_file(source_path: str) -> Optional[str]:
    """
    Copy file Final Project.csv (do giảng viên cung cấp) sang data/raw/
    để bước wrangling phía sau dễ tìm. Hỗ trợ cả .csv lẫn .xlsx.

    Args:
        source_path: Đường dẫn tới file gốc.

    Returns:
        Đường dẫn file đã được copy, hoặc None nếu file không tồn tại.
    """
    if not source_path or not os.path.exists(source_path):
        log.warning("Không tìm thấy file khảo sát tại: %s", source_path)
        return None

    # Đặt tên chuẩn để wrangling tìm được
    ext = os.path.splitext(source_path)[1].lower()
    dest_name = "survey_raw.csv" if ext == ".csv" else f"survey_raw{ext}"
    dest_path = os.path.join(RAW_DIR, dest_name)

    shutil.copy2(source_path, dest_path)
    log.info("Đã copy file khảo sát -> %s", dest_path)

    # In thử shape để kiểm tra nhanh
    try:
        if ext == ".csv":
            df_preview = pd.read_csv(dest_path, low_memory=False, nrows=5)
        else:
            df_preview = pd.read_excel(dest_path, nrows=5)
        log.info("File khảo sát có %d cột. 5 cột đầu: %s",
                 df_preview.shape[1], list(df_preview.columns[:5]))
    except Exception as err:
        log.warning("Không preview được file: %s", err)

    return dest_path


# =============================================================================
# 5. HÀM CHÍNH
# =============================================================================
def main(survey_path: Optional[str] = None, max_pages: int = 50) -> None:
    """
    Pipeline thu thập:
        1) Stage file khảo sát Final Project.csv
        2) Scrape ItViec
        3) Lưu kết quả vào data/raw/
    """
    log.info("====== BẮT ĐẦU THU THẬP DỮ LIỆU ======")

    # ---- (1) File khảo sát ----
    # Mặc định tìm file ở data/raw/Final Project.csv, nếu user truyền path khác
    # thì dùng path đó.
    if survey_path is None:
        candidate = os.path.join(RAW_DIR, "Final Project.csv")
        survey_path = candidate if os.path.exists(candidate) else None

    if survey_path:
        stage_survey_file(survey_path)
    else:
        log.warning(
            "Chưa có file khảo sát. Hãy đặt 'Final Project.csv' vào %s "
            "trước khi chạy bước wrangling.", RAW_DIR,
        )

    # ---- (2) Scrape ItViec ----
    df_itviec = scrape_itviec(max_pages=max_pages)
    if not df_itviec.empty:
        out_path = os.path.join(RAW_DIR, "itviec_jobs_raw.csv")
        df_itviec.to_csv(out_path, index=False, encoding="utf-8-sig")
        log.info("Đã lưu %d job ItViec -> %s", len(df_itviec), out_path)
    else:
        log.warning("Không scrape được dữ liệu ItViec.")

    log.info("====== HOÀN TẤT THU THẬP ======")


if __name__ == "__main__":
    # Ví dụ chạy: python 01_data_collection.py
    # Có thể chỉnh max_pages để giới hạn thời gian chạy khi demo.
    main(max_pages=50)
