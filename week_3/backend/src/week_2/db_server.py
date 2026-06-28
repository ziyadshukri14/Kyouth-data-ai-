import os
import sqlite3
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("SQLite-Service")

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "jobs.db"
DB_PATH = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))


@mcp.tool
def read_jobs(include_tagged: bool = False) -> list:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        if include_tagged:
            query = """
                SELECT source_id, description, tech_stack
                FROM jobs
            """
        else:
            query = """
                SELECT source_id, description
                FROM jobs
                WHERE tech_stack IS NULL
                   OR TRIM(tech_stack) = ''
            """

        cursor.execute(query)
        return cursor.fetchall()


@mcp.tool
def update_tech_stack(source_id: str, tech_stack: str) -> str:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE jobs
            SET tech_stack = ?
            WHERE source_id = ?
            """,
            (tech_stack, source_id),
        )

        connection.commit()

    return f"Tech stack updated for {source_id}"


@mcp.tool
def get_all_tech_stacks() -> list:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT source_id, tech_stack
            FROM jobs
            WHERE tech_stack IS NOT NULL
              AND TRIM(tech_stack) != ''
              AND tech_stack != 'no tech stack extracted'
            """
        )

        return cursor.fetchall()


@mcp.tool
def get_job_count() -> dict:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM jobs")
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM jobs
            WHERE tech_stack IS NOT NULL
              AND TRIM(tech_stack) != ''
            """
        )
        tagged = cursor.fetchone()[0]

    return {
        "total": total,
        "tagged": tagged,
    }


if __name__ == "__main__":
    mcp.run()