"""
data_quality.py — Kiểm tra chất lượng dữ liệu CSV và sinh báo cáo.

Các tiêu chí được check (xem QUALITY_THRESHOLDS trong config.py):
    1. Tổng số job >= min_jobs_per_run
    2. Tỷ lệ status='ok' >= min_ok_ratio
    3. Tỷ lệ job có skill nhận diện >= min_skill_coverage
    4. Tuổi dữ liệu mới nhất <= max_data_age_days
    5. Không có giá trị bất thường (salary âm, scrape_date tương lai, ...)

Exit code:
    0  -> PASS
    1  -> WARN (có cảnh báo nhưng dữ liệu vẫn dùng được)
    2  -> FAIL (dữ liệu lỗi nghiêm trọng)

Run:
    python scripts/data_quality.py
    python scripts/data_quality.py --report quality_report.md
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CSV_PATH, QUALITY_THRESHOLDS
from csv_writer import read_csv

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Các check con
# -----------------------------------------------------------------------------
def _latest_date(rows: list[dict]) -> str:
    return max((r.get("scrape_date", "") for r in rows), default="")


def check_total_jobs(rows: list[dict]) -> dict:
    """Check #1: số job tối thiểu trong lần scrape mới nhất."""
    if not rows:
        return {"name": "total_jobs", "status": "FAIL",
                "msg": "CSV rỗng"}

    latest = _latest_date(rows)
    today_jobs = [r for r in rows if r.get("scrape_date") == latest]
    n = len(today_jobs)
    lo, hi = QUALITY_THRESHOLDS["min_jobs_per_run"], QUALITY_THRESHOLDS["max_jobs_per_run"]

    if n < lo:
        return {"name": "total_jobs", "status": "WARN",
                "msg": f"Ngày {latest}: chỉ {n} job (< {lo})"}
    if n > hi:
        return {"name": "total_jobs", "status": "WARN",
                "msg": f"Ngày {latest}: {n} job (> {hi}) - nghi scrape lặp"}
    return {"name": "total_jobs", "status": "PASS",
            "msg": f"Ngày {latest}: {n} job (trong khoảng [{lo}, {hi}])"}


def check_ok_ratio(rows: list[dict]) -> dict:
    """Check #2: tỷ lệ row status='ok' so với tổng."""
    if not rows:
        return {"name": "ok_ratio", "status": "FAIL", "msg": "CSV rỗng"}

    n_ok = sum(1 for r in rows if r.get("status") == "ok")
    ratio = n_ok / len(rows)
    thresh = QUALITY_THRESHOLDS["min_ok_ratio"]

    status = "PASS" if ratio >= thresh else "WARN"
    return {"name": "ok_ratio", "status": status,
            "msg": f"{n_ok}/{len(rows)} = {ratio:.1%} (ngưỡng {thresh:.0%})"}


def check_skill_coverage(rows: list[dict]) -> dict:
    """Check #3: tỷ lệ row có cột skills không rỗng."""
    if not rows:
        return {"name": "skill_coverage", "status": "FAIL", "msg": "CSV rỗng"}

    n_with = sum(1 for r in rows if (r.get("skills") or "").strip())
    ratio = n_with / len(rows)
    thresh = QUALITY_THRESHOLDS["min_skill_coverage"]

    status = "PASS" if ratio >= thresh else "WARN"
    return {"name": "skill_coverage", "status": status,
            "msg": f"{n_with}/{len(rows)} = {ratio:.1%} (ngưỡng {thresh:.0%})"}


def check_data_age(rows: list[dict]) -> dict:
    """Check #4: tuổi dữ liệu mới nhất."""
    if not rows:
        return {"name": "data_age", "status": "FAIL", "msg": "CSV rỗng"}

    latest = _latest_date(rows)
    try:
        latest_date = date.fromisoformat(latest)
    except ValueError:
        return {"name": "data_age", "status": "FAIL",
                "msg": f"scrape_date không hợp lệ: {latest}"}

    age_days = (date.today() - latest_date).days
    thresh = QUALITY_THRESHOLDS["max_data_age_days"]
    status = "PASS" if age_days <= thresh else "FAIL"
    return {"name": "data_age", "status": status,
            "msg": f"Dữ liệu mới nhất {age_days} ngày trước (ngưỡng {thresh} ngày)"}


def check_anomalies(rows: list[dict]) -> dict:
    """Check #5: phát hiện giá trị bất thường."""
    issues: list[str] = []
    today_iso = date.today().isoformat()

    for r in rows:
        # scrape_date không được lớn hơn hôm nay
        if r.get("scrape_date", "") > today_iso:
            issues.append(f"scrape_date tương lai: {r.get('scrape_date')}")

        # salary âm hoặc quá lớn
        for col in ("salary_min_usd", "salary_max_usd"):
            v = r.get(col, "")
            if not v:
                continue
            try:
                fv = float(v)
                if fv < 0 or fv > 100000:
                    issues.append(f"{col} bất thường: {fv}")
            except ValueError:
                issues.append(f"{col} không phải số: {v!r}")

        if len(issues) >= 5:
            issues.append("(... và nhiều hơn nữa)")
            break

    if issues:
        return {"name": "anomalies", "status": "WARN",
                "msg": "; ".join(issues[:5])}
    return {"name": "anomalies", "status": "PASS", "msg": "Không phát hiện bất thường"}


# -----------------------------------------------------------------------------
# Tổng hợp & sinh báo cáo
# -----------------------------------------------------------------------------
ALL_CHECKS = (
    check_total_jobs,
    check_ok_ratio,
    check_skill_coverage,
    check_data_age,
    check_anomalies,
)


def run_all_checks(csv_path: Path) -> tuple[int, list[dict]]:
    rows = read_csv(csv_path)
    log.info("Loaded %d rows from %s", len(rows), csv_path)

    results = [chk(rows) for chk in ALL_CHECKS]

    # Tính exit code tổng
    if any(r["status"] == "FAIL" for r in results):
        code = 2
    elif any(r["status"] == "WARN" for r in results):
        code = 1
    else:
        code = 0
    return code, results


def render_markdown(results: list[dict], csv_path: Path) -> str:
    """Sinh báo cáo Markdown gọn để post lên Telegram / artifact."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# ItViec Data Quality Report",
        f"_Generated at {now}_",
        f"_CSV: `{csv_path}`_",
        "",
        "| Check | Status | Message |",
        "|---|---|---|",
    ]
    for r in results:
        emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(r["status"], "?")
        lines.append(f"| {r['name']} | {emoji} {r['status']} | {r['msg']} |")
    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="ItViec data quality check")
    parser.add_argument("--csv", default=str(CSV_PATH))
    parser.add_argument("--report", help="Đường dẫn file .md để ghi báo cáo")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        log.warning("CSV chưa tồn tại: %s", csv_path)
        return 1

    code, results = run_all_checks(csv_path)

    # In ra console
    for r in results:
        log.info("[%-4s] %-15s | %s", r["status"], r["name"], r["msg"])
    log.info("\nExit code: %d", code)

    # Ghi báo cáo nếu được yêu cầu
    if args.report:
        Path(args.report).write_text(render_markdown(results, csv_path),
                                     encoding="utf-8")
        log.info("Đã ghi báo cáo: %s", args.report)

    return code


if __name__ == "__main__":
    sys.exit(main())
