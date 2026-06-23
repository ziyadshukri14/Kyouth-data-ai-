import os
import sqlite3

from fastmcp import FastMCP

mcp = FastMCP("SQLite-Service")

DB_PATH = os.getenv("DB_PATH", "jobs_d1.db")


@mcp.tool
def read_jobs(include_tagged: bool = False) -> list:
    """Retrieve job records from the database."""

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
                   OR tech_stack = ''
            """

        cursor.execute(query)
        records = cursor.fetchall()

    return records


@mcp.tool
def update_tech_stack(source_id: str, tech_stack: str) -> str:
    """Save extracted technologies for a job."""

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
    """Return all rows that contain a valid tech stack."""

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT source_id, tech_stack
            FROM jobs
            WHERE tech_stack IS NOT NULL
              AND tech_stack != ''
              AND tech_stack != 'no tech stack extracted'
            """
        )

        rows = cursor.fetchall()

    return rows


@mcp.tool
def get_job_count() -> dict:
    """Return total jobs and tagged jobs."""

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM jobs
            WHERE tech_stack IS NOT NULL
              AND tech_stack != ''
            """
        )

        tagged_jobs = cursor.fetchone()[0]

    return {
        "total": total_jobs,
        "tagged": tagged_jobs,
    }


if __name__ == "__main__":
    mcp.run()
