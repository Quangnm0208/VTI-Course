"""
analyze_skills.py — Kiểm tra chất lượng skill_report + mức lương.

Mục đích:
    Trả lời câu hỏi: "Job nào có kỹ năng quan trọng VÀ có mức lương?"

Chạy:
    python scripts/analyze_skills.py
    python scripts/analyze_skills.py --top 20 --skill Python
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CSV_PATH

# Kỹ năng quan trọng theo phân tích tổng hợp (Stack Overflow + ItViec)
IMPORTANT_SKILLS = {
    "language":     ["JavaScript", "Python", "Java", "TypeScript", "C#", "SQL",
                     "Go", "Kotlin", "PHP", "C++"],
    "database":     ["MySQL", "PostgreSQL", "MongoDB", "Redis", "SQL Server",
                     "Oracle"],
    "framework":    ["ReactJS", "React", "Angular", "Vue", "Spring Boot",
                     "Django", "Node.js", "Laravel", ".NET"],
    "cloud_devops": ["AWS", "Azure", "Docker", "Kubernetes", "Jenkins",
                     "Google Cloud"],
}
ALL_IMPORTANT = {s for cat in IMPORTANT_SKILLS.values() for s in cat}


def load_and_explode(csv_path: Path) -> pd.DataFrame:
    """Đọc CSV và explode cột skills thành long-format (1 dòng = 1 skill)."""
    df = pd.read_csv(csv_path)
    df["skills_list"] = df["skills"].fillna("").astype(str).str.split(";")
    long_df = df.explode("skills_list")
    long_df["skill"] = long_df["skills_list"].str.strip()
    long_df = long_df[long_df["skill"] != ""]
    return long_df


def has_real_salary(df: pd.DataFrame) -> pd.Series:
    """Trả về mask: True nếu job có lương thực (không phải 'Sign in...' hoặc 'Negotiable')."""
    s = df["salary"].fillna("").astype(str).str.lower()
    is_fake = s.str.contains("sign in") | s.str.contains("negotiable") | (s == "")
    has_min = df["salary_min_usd"].notna() & (df["salary_min_usd"] != "")
    return (~is_fake) | has_min


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(CSV_PATH))
    parser.add_argument("--top", type=int, default=15, help="Top N kỹ năng")
    parser.add_argument("--skill", help="Lọc theo 1 kỹ năng cụ thể (vd Python)")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    df = pd.read_csv(csv_path)
    n_total = len(df)
    print(f"════════════════════════════════════════════════════════════════")
    print(f"  ITVIEC SKILL REPORT — {n_total} jobs (scraped {df['scrape_date'].max()})")
    print(f"════════════════════════════════════════════════════════════════\n")

    # ----- 1. THỐNG KÊ CƠ BẢN -----
    print("📊 1. THỐNG KÊ CƠ BẢN")
    print(f"   • Job có cột skills không rỗng : {(df['skills'].fillna('').astype(str).str.strip() != '').sum():>4d}/{n_total}")
    sal_mask = has_real_salary(df)
    print(f"   • Job có lương THỰC TẾ          : {sal_mask.sum():>4d}/{n_total} ({sal_mask.sum()*100/n_total:.1f}%)")
    print(f"   • Job 'Sign in to view salary' : {(~sal_mask).sum():>4d}/{n_total} ({(~sal_mask).sum()*100/n_total:.1f}%)")
    n_company = df["company"].notna().sum()
    print(f"   • Job có tên công ty            : {n_company:>4d}/{n_total} ({n_company*100/n_total:.1f}%)")
    print()

    # ----- 2. TOP KỸ NĂNG -----
    long_df = load_and_explode(csv_path)
    skill_counts = long_df["skill"].value_counts().head(args.top)
    print(f"📈 2. TOP {args.top} KỸ NĂNG XUẤT HIỆN NHIỀU NHẤT")
    for i, (skill, count) in enumerate(skill_counts.items(), 1):
        is_imp = "⭐" if skill in ALL_IMPORTANT else "  "
        print(f"   {i:>2}. {is_imp} {skill:<25s} {count:>4d} jobs ({count*100/n_total:5.1f}%)")
    print(f"\n   ⭐ = kỹ năng nằm trong danh sách QUAN TRỌNG đã định nghĩa\n")

    # ----- 3. JOB CÓ SKILL QUAN TRỌNG + LƯƠNG THỰC -----
    print(f"💰 3. JOB CÓ KỸ NĂNG QUAN TRỌNG + LƯƠNG THỰC")
    important_pattern = "|".join(ALL_IMPORTANT)
    has_imp = df["skills"].fillna("").str.contains(important_pattern, regex=True, case=False)
    has_sal = has_real_salary(df)
    qualified = df[has_imp & has_sal]
    print(f"   Tổng số job đạt cả 2 điều kiện: {len(qualified)}/{n_total}\n")
    if len(qualified) > 0:
        sample = qualified[["job_title", "company", "salary", "skills"]].head(10)
        for _, row in sample.iterrows():
            print(f"   • {row['job_title'][:55]:<55s}")
            print(f"     💼 {str(row.get('company') or 'N/A')[:40]:<40s}  💵 {row['salary']}")
            skills_show = row['skills'][:80] + ("..." if len(row['skills']) > 80 else "")
            print(f"     🔧 {skills_show}\n")

    # ----- 4. LỌC THEO 1 SKILL CỤ THỂ (nếu user truyền --skill) -----
    if args.skill:
        print(f"🔍 4. JOB CHỨA KỸ NĂNG: '{args.skill}'")
        mask = df["skills"].fillna("").str.contains(args.skill, case=False, regex=False)
        sub = df[mask]
        print(f"   Tổng: {len(sub)} jobs")
        print(f"   Có lương thực: {has_real_salary(sub).sum()}\n")
        for _, row in sub.head(15).iterrows():
            print(f"   • {row['job_title'][:60]:<60s} | {row['salary']}")
        print()

    # ----- 5. PHÂN BỔ THEO NHÓM SKILL -----
    print("📂 5. PHÂN BỔ JOB THEO NHÓM SKILL")
    for category, skill_list in IMPORTANT_SKILLS.items():
        pattern = "|".join(skill_list)
        n_jobs = df["skills"].fillna("").str.contains(pattern, regex=True, case=False).sum()
        print(f"   • {category:<15s}: {n_jobs:>4d} jobs ({n_jobs*100/n_total:5.1f}%)")
    print()


if __name__ == "__main__":
    main()
