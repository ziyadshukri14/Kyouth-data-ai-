import sqlite3
from pathlib import Path


def run_data_profile(db_path):
    db_path = Path(db_path)

    print("\n🔍 DATA QUALITY REPORT ---")

    # ❌ database missing safety check
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Total records
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]

    # 2. NULL checks
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN job_title IS NULL OR job_title = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN company IS NULL OR company = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END)
        FROM jobs
    """)
    null_job_title, null_company, null_description = cursor.fetchone()

    # 3. Average description length
    cursor.execute("""
        SELECT AVG(LENGTH(description)) FROM jobs
    """)
    avg_desc = cursor.fetchone()[0] or 0

    # 4. Shortest description
    cursor.execute("""
        SELECT source_id, job_title, LENGTH(description)
        FROM jobs
        ORDER BY LENGTH(description) ASC
        LIMIT 1
    """)
    shortest = cursor.fetchone()

    # 5. Longest description
    cursor.execute("""
        SELECT source_id, job_title, LENGTH(description)
        FROM jobs
        ORDER BY LENGTH(description) DESC
        LIMIT 1
    """)
    longest = cursor.fetchone()

    conn.close()

    # OUTPUT FORMAT
    print(f"📈 Total Records: {total}")
    print(f"❓ Missing Values -> job_title: {null_job_title}, company: {null_company}, description: {null_description}")
    print(f"📝 Avg Description Length: {int(avg_desc)} chars")

    if shortest:
        print(f"⚠️ Shortest Description: {shortest[2]} chars")
        print(f"   ↳ source_id: {shortest[0]} | job_title: {shortest[1]}")

    if longest:
        print(f"🚨 Longest Description: {longest[2]} chars")
        print(f"   ↳ source_id: {longest[0]} | job_title: {longest[1]}")