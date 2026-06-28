import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from week_2.find_skill_gaps import find_skill_gaps

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

load_dotenv()
load_dotenv(PROJECT_DIR / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:8000",
        "http://0.0.0.0",
        "http://0.0.0.0:80",
        "http://0.0.0.0:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = PROJECT_DIR / "data" / "jobs.db"


class ChatRequest(BaseModel):
    message: str = ""
    pdf_text: str = ""


@app.get("/")
def root():
    return {
        "status": "Backend server is running",
        "database": str(DB_PATH),
        "database_exists": DB_PATH.exists(),
    }


@app.post("/chat")
def chat(request: ChatRequest):
    temp_resume_path = None

    try:
        user_text = request.message.strip()
        pdf_text = request.pdf_text.strip()

        combined_text = ""

        if pdf_text:
            combined_text += pdf_text

        if user_text:
            combined_text += "\n\nUser question:\n" + user_text

        if not combined_text.strip():
            return JSONResponse(
                content={
                    "reply": "Please enter a message or upload a resume PDF."
                }
            )

        if not DB_PATH.exists():
            return JSONResponse(
                status_code=500,
                content={
                    "reply": f"Database not found: {DB_PATH}"
                },
            )

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(combined_text)
            temp_resume_path = temp_file.name

        result = find_skill_gaps(
            input_file_path=temp_resume_path,
            db_url=str(DB_PATH),
        )

        missing_skills = (
            ", ".join(result.gaps[:20])
            if result.gaps
            else "None"
        )

        top_missing = (
            ", ".join(result.top_missing_skills)
            if result.top_missing_skills
            else "None"
        )

        reply = (
            "Skill Gap Analysis Completed.\n\n"
            f"Missing skills: {missing_skills}\n\n"
            f"Top missing skills: {top_missing}\n\n"
            f"Tokens used: {result.tokens}\n"
            f"Time used: {result.time} ms"
        )

        return {"reply": reply}

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "reply": f"Backend error: {error}"
            },
        )

    finally:
        if temp_resume_path:
            Path(temp_resume_path).unlink(missing_ok=True)