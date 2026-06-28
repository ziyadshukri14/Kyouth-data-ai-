import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.templating import Jinja2Templates
from pypdf import PdfReader

load_dotenv()

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001/chat")

DB_PATH = Path(
    os.getenv(
        "DB_PATH",
        str(PROJECT_DIR / "data" / "jobs.db"),
    )
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={
            "backend_url": BACKEND_URL,
        },
    )


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={},
    )


@app.get("/test-db")
def test_db():
    try:
        return {
            "db_path": str(DB_PATH),
            "db_exists": DB_PATH.exists(),
            "parent_exists": DB_PATH.parent.exists(),
        }
    except Exception as error:
        return {
            "error": str(error),
        }


def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    return sqlite3.connect(DB_PATH)


@app.get("/api/jobs")
def search_jobs(q: str = ""):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT source_id, job_title, company, description
                FROM jobs
                WHERE job_title LIKE ?
                   OR company LIKE ?
                   OR description LIKE ?
                ORDER BY source_id
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%"),
            )

            rows = cursor.fetchall()

        return {
            "jobs": [
                {
                    "source_id": row[0],
                    "job_title": row[1],
                    "company": row[2],
                    "description": row[3][:250] if row[3] else "",
                }
                for row in rows
            ]
        }

    except Exception as error:
        return {
            "jobs": [],
            "error": str(error),
            "db_path": str(DB_PATH),
            "db_exists": DB_PATH.exists(),
        }


@app.get("/api/charts")
def chart_data():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT company, COUNT(*) AS total
                FROM jobs
                WHERE company IS NOT NULL
                  AND TRIM(company) != ''
                GROUP BY company
                ORDER BY total DESC
                LIMIT 10
                """
            )
            company_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT job_title, COUNT(*) AS total
                FROM jobs
                WHERE job_title IS NOT NULL
                  AND TRIM(job_title) != ''
                GROUP BY job_title
                ORDER BY total DESC
                LIMIT 10
                """
            )
            title_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    CASE
                        WHEN LENGTH(description) < 1000 THEN 'Short'
                        WHEN LENGTH(description) BETWEEN 1000 AND 3000 THEN 'Medium'
                        ELSE 'Long'
                    END AS description_length,
                    COUNT(*) AS total
                FROM jobs
                GROUP BY description_length
                ORDER BY total DESC
                """
            )
            description_rows = cursor.fetchall()

        return {
            "companies": {
                "labels": [row[0] for row in company_rows],
                "values": [row[1] for row in company_rows],
            },
            "titles": {
                "labels": [row[0] for row in title_rows],
                "values": [row[1] for row in title_rows],
            },
            "descriptions": {
                "labels": [row[0] for row in description_rows],
                "values": [row[1] for row in description_rows],
            },
        }

    except Exception as error:
        return {
            "companies": {"labels": [], "values": []},
            "titles": {"labels": [], "values": []},
            "descriptions": {"labels": [], "values": []},
            "error": str(error),
            "db_path": str(DB_PATH),
            "db_exists": DB_PATH.exists(),
        }


@app.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    try:
        pdf_reader = PdfReader(file.file)
        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

        return {"text": text.strip()}

    except Exception as error:
        return {
            "text": "",
            "error": str(error),
        }