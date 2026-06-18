from pathlib import Path
import sqlite3
import json


def load_all_jsons(input_dir, output_dir):

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    print("🥇 Gold:...\n")

    # Create output folder if missing
    output_path.mkdir(parents=True, exist_ok=True)

    # Check if silver folder exists
    if not input_path.exists():

        print("⚠️ Input directory does not exist")

        print("\n📊 Gold Summary:")
        print("Total: 0 | Inserted: 0 | Skipped: 0")
        return

    # Get all JSON files
    files = list(input_path.glob("*.json"))

    if len(files) == 0:

        print("⚠️ No JSON files found")

        print("\n📊 Gold Summary:")
        print("Total: 0 | Inserted: 0 | Skipped: 0")
        return

    total = len(files)
    inserted = 0
    skipped = 0

    # Create database jobs
    db_file = output_path / "jobs.db"

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Create table
    # source_id is PRIMARY KEY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs(

            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT,
            tech_stack TEXT
        )
    """)

    # Read JSON files one by one
    for file_path in files:

        try:

            # open json
            data = json.loads(
                file_path.read_text(encoding="utf-8")
            )

            # insert into database
            cursor.execute("""
                INSERT OR IGNORE INTO jobs

                (source_id, job_title, company, description, tech_stack)

                VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["source_id"],
                data["job_title"],
                data["company"],
                data["description"],
                None
            ))

            # check if inserted
            if cursor.rowcount == 1:

                print(f"✅ Inserted: {file_path.name}")
                inserted += 1

            else:

                print(f"⏭️ Skipped (duplicate): {file_path.name}")
                skipped += 1

        except Exception:

            print(f"❌ Failed: {file_path.name}")
            skipped += 1

    # Save database
    connection.commit()

    # Close database
    connection.close()

    # Final summary
    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")