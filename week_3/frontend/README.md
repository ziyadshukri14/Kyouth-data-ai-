# Week 3: Full-Stack AI Resume Skill Gap Analyzer

A containerized AI-powered web application that integrates the data engineering pipeline from Week 1 and the AI skill extraction module from Week 2 into a complete microservices architecture.

---

# Project Overview

This project combines multiple components developed throughout the K-Youth FX Digital Skills Program into a single deployable application.

The system consists of a **FastAPI frontend**, a **FastAPI backend**, and a **SQLite database**, with each service running independently inside Docker containers and communicating through Docker Compose.

Users can:

- Upload a PDF resume
- Enter resume skills through a chatbot
- Receive AI-generated skill gap analysis

The backend uses **Google Gemini** to extract technical skills from resumes and compares them with skills extracted from real Malaysian technology job listings collected during Week 1.

---

# Main Features

### AI Chat Assistant

- Chat-based interface
- Resume skill analysis
- JSON communication between frontend and backend

### Resume Upload

- Upload PDF resumes
- Automatic text extraction using PDF.js
- Resume content sent directly to backend

### Skill Gap Detection

- AI extracts technical skills
- Compares resume against Week 1 database
- Returns:
  - Missing skills
  - Top missing skills
  - Token usage
  - Processing time

### Job Dashboard

Interactive Charts.js dashboard including:

- Company distribution
- Job title distribution
- Description length statistics
- Searchable jobs database

---

# Project Structure

```text
week_3
│
├── frontend
│   ├── src
│   ├── templates
│   ├── data
│   └── Dockerfile
│
├── backend
│   ├── src
│   ├── week_2
│   ├── data
│   │     └── jobs.db
│   └── Dockerfile
│
└── docker-compose.yml
```

---

# Requirements

Before running the project, ensure you have:

- Docker Desktop
- Docker Compose
- Google Gemini API Key
- Python 3.14 (optional for local development)
- UV Package Manager

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/ziyadshukri14/Kyouth-data-ai-

cd kyouth-data-ai/week_3
```

---

## 2. Configure Backend Environment

Create:

```text
backend/.env
```

Add:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

---

## 3. Configure Frontend Environment

Create:

```text
frontend/.env
```

Add:

```env
BACKEND_URL=http://localhost:8001/chat
```

---

## 4. Prepare Database

Ensure the SQLite database is available at:

```text
week_3/backend/data/jobs.db
```

If the database has not been tagged with technical skills, execute the Week 2 tagging pipeline first.

Example:

```bash
cd week_2

uv run tag_data.py
```

---

## 5. Build Docker Containers

```bash
docker compose up --build
```

Docker Compose automatically builds:

- Frontend Container
- Backend Container

Both containers communicate through the Docker bridge network.

---

# Running the Application

After Docker finishes building:

Frontend

```text
http://localhost
```

Backend

```text
http://localhost:8001
```

Dashboard

```text
http://localhost/dashboard
```

Landing Page (Bonus)

```text
http://localhost:8080
```

---

# Application Workflow

1. User uploads a resume PDF or types their skills.
2. Frontend extracts PDF text using PDF.js.
3. The frontend sends the request as JSON.
4. Backend receives the request through the `/chat` endpoint.
5. Google Gemini extracts technical skills from the resume.
6. Backend compares extracted skills against `jobs.db`.
7. Missing skills are ranked according to job market demand.
8. Results are returned to the frontend and displayed inside the chatbot.

---

# Technologies Used

### Frontend

- FastAPI
- Bootstrap 5
- Jinja2
- JavaScript
- PDF.js

### Backend

- FastAPI
- Python
- Google Gemini API
- SQLite

### Data Processing

- BeautifulSoup
- Pydantic
- AsyncIO
- FastMCP

### Data Visualization

- Charts.js

### DevOps

- Docker
- Docker Compose
- Railway

---

# System Architecture

```text
                 User Browser
                      │
                      ▼
        Frontend Container (FastAPI)
                      │
          HTML • Bootstrap • Jinja2
                      │
         POST /chat (JSON Request)
                      ▼
        Backend Container (FastAPI)
                      │
          find_skill_gaps()
                      │
        Google Gemini API
                      │
              SQLite jobs.db
                      │
         Skill Gap Analysis
                      ▼
           Response to Frontend
```

---

# Future Enhancements

- User authentication
- Resume history
- Multiple AI model support
- Live job scraping
- Personalized career recommendations
- Resume scoring system

---

## Usage

### Run with Docker Compose (Recommended)

From the project root:

```bash
cd week_3
docker compose up --build
```

Once the containers have started, open:

- **Frontend (Chat Application):** http://localhost:8000
- **Backend API:** http://localhost:8001
- **Job Dashboard:** http://localhost:8000/dashboard

---

### Run Locally (Without Docker)

#### 1. Start the Backend

```bash
cd week_3/backend
uv sync
uv run uvicorn --app-dir src app:app --host 0.0.0.0 --port 8001
```

Create a `.env` file inside `week_3/backend`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

#### 2. Start the Frontend

Open a new terminal:

```bash
cd week_3/frontend
uv sync
uv run uvicorn --app-dir src app:app --host 0.0.0.0 --port 8000
```

Create a `.env` file inside `week_3/frontend`:

```env
BACKEND_URL=http://localhost:8001/chat
```

---

### Access the Application

After both services are running, open your browser and navigate to:

- **Chat Application:** http://localhost:8000
- **Job Dashboard:** http://localhost:8000/dashboard
- **Backend API Documentation:** http://localhost:8001/docs

The chat application allows users to upload a PDF resume or enter resume text manually. The frontend sends the extracted text to the backend, which performs AI-powered skill gap analysis using the Week 1 jobs database and returns the missing skills and most in-demand technologies.

## Expected Inputs and Outputs

### Text Input

Type your skills or paste your resume text into the chat box, then click **Send**.

**Example Input**

```text
I have experience with Python, SQL, Pandas, NumPy, Power BI, Git, and data visualization.
```

**Example Output**

```text
Skill Gap Analysis Completed.

Missing Skills:
AWS, Docker, Kubernetes, FastAPI, Azure, CI/CD

Top Missing Skills:
AWS, Docker, Azure, GitHub Actions, Kubernetes

Tokens Used:
72

Processing Time:
1.84 seconds
```

---

### PDF Resume Input

Click the **Upload** button and select a PDF resume. The application extracts the resume text automatically using **PDF.js**, then sends it together with your prompt to the backend for analysis.

**Example Input**

```text
Resume.pdf
```

**Example Output**

```text
Skill Gap Analysis Completed.

Missing Skills:
Docker, Terraform, Kubernetes, Apache Kafka, Databricks

Top Missing Skills:
Docker, Kubernetes, AWS, Terraform, Kafka

Tokens Used:
95

Processing Time:
2.13 seconds
```

## API / Function Reference

### Backend API

#### `POST /chat`

**URL**

```text
http://localhost:8001/chat
```

**Request (JSON)**

```json
{
  "message": "I know Python, SQL, and pandas",
  "pdf_text": ""
}
```

If `pdf_text` is provided, it is used as the resume source instead of the typed message.

**Response (JSON)**

```json
{
  "reply": "Skill Gap Analysis Completed.\n\nMissing Skills: AWS, Docker, Kubernetes...\n\nTop Missing Skills: AWS, Docker, Git, Azure, FastAPI\n\nTokens Used: 72\nTime Used: 1.84 seconds"
}
```

### Backend Request Flow

1. Receives the JSON request from the frontend.
2. Creates a temporary text file containing the resume content.
3. Calls `find_skill_gaps(temp_file_path, jobs.db)`.
4. Extracts resume skills using Gemini.
5. Retrieves required job skills from the Week 1 SQLite database.
6. Compares resume skills with job requirements.
7. Returns the missing skills as a JSON response.
8. Deletes the temporary file.

---

## Frontend API Endpoints

| Endpoint              | Method | Description                              |
| --------------------- | ------ | ---------------------------------------- |
| `/`                   | GET    | Displays the chat interface              |
| `/dashboard`          | GET    | Displays the job dashboard               |
| `/api/charts`         | GET    | Returns data for Chart.js visualizations |
| `/api/jobs?q=<query>` | GET    | Searches the jobs database               |
| `/extract-pdf`        | POST   | Extracts text from an uploaded PDF       |

---

## JavaScript Functions

### `sendMessage()`

- Reads the user's text input.
- Includes extracted PDF text if available.
- Sends a JSON request to the backend.
- Displays the backend response inside the chat window.
- Clears the input field after sending.

---

### `addMessage(text, sender)`

- Creates a chat bubble.
- Displays either a user message or bot response.
- Automatically scrolls to the newest message.

---

### PDF Upload Handler

- Detects when a PDF is selected.
- Uses **PDF.js** to extract text from every page.
- Stores the extracted text for the next chat request.

---

## Data Flow

```text
User types a message or uploads a PDF
            │
            ▼
Frontend (Chat Page)
    │
    ├── PDF.js extracts text (if a PDF is uploaded)
    ├── Creates JSON request
    ▼
POST /chat
            │
            ▼
Backend (FastAPI)
    │
    ├── Creates temporary text file
    ├── Calls find_skill_gaps()
    ▼
Week 2 AI Module
    │
    ├── Gemini extracts resume skills
    ├── Reads job tech stacks from jobs.db
    ├── Compares resume skills with database skills
    ▼
Returns missing skills
            │
            ▼
Frontend displays the response as a chat message
```

---

## Data Assumptions

- Messages between the frontend and backend follow this JSON format:

```json
{
  "message": "User entered text",
  "pdf_text": "Extracted PDF content"
}
```

- PDF files are processed entirely in the browser before being sent.
- Resume text is sanitized before being processed by Gemini.
- The `jobs.db` database must contain populated `tech_stack` values.
- User input is treated as resume content for skill gap analysis.
- Each request is processed independently without conversation history.

---

## Constraints

- Very large PDF files may take longer to process.
- Gemini free-tier usage is limited by daily request quotas.
- The displayed response shows only the first 20 missing skills.
- Internet connectivity is required to access the Gemini API.

---

## Testing

### Frontend Testing

| Test Case   | Steps                              | Expected Result                    |
| ----------- | ---------------------------------- | ---------------------------------- |
| Send text   | Enter skills and click **Send**    | Skill gap analysis is displayed    |
| Press Enter | Type a message and press **Enter** | Same result as clicking **Send**   |
| Upload PDF  | Select a PDF and send              | PDF text is extracted and analyzed |
| Empty input | Click **Send** without input       | No request is sent                 |
| Dashboard   | Open `/dashboard`                  | Charts load successfully           |
| Search jobs | Enter a keyword                    | Matching jobs are displayed        |

---

### Backend Testing

Test the backend directly:

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I know Python, SQL, and pandas","pdf_text":""}'
```

Example response:

```json
{
  "reply": "Skill Gap Analysis Completed..."
}
```

---

### Docker Communication Test

Start the application:

```bash
docker compose up
```

Then send a request through the frontend.

Docker logs should show successful communication between both services:

```text
frontend-1 | POST /chat
backend-1  | POST /chat 200 OK
```

---

## Limitations

- Conversation history is not stored.
- User authentication is not implemented.
- Gemini API usage depends on free-tier quotas.
- Temporary Gemini service interruptions (HTTP 503) may occur during high demand.
- Skill matching is based on exact string comparison.
- The application requires a populated `jobs.db` database.
- Complex PDF layouts may reduce text extraction accuracy.
- Refreshing the page clears the chat history.

---

## Architecture Reflection

### Design Choices

The application follows a microservices architecture consisting of separate frontend and backend services.

The frontend is responsible for rendering the user interface, handling PDF uploads, and communicating with the backend. The backend performs AI-powered skill gap analysis, interacts with the database, and processes all business logic.

Each service has its own Docker container and dependency set, allowing independent development, deployment, and maintenance.

Containerization ensures a consistent runtime environment across different machines.

---

### Trade-offs

- Docker Compose simplifies deployment but is intended primarily for development environments.
- Using Gemini provides high-quality AI responses while introducing API rate limits and internet dependency.
- The dashboard accesses the SQLite database directly through the frontend service, reducing architectural complexity.

---

## Future Improvements

- Store chat history using a database.
- Stream AI responses using Server-Sent Events.
- Improve skill matching with semantic embeddings.
- Deploy the application on Railway or Render.
- Add user authentication and personal profiles.
- Support additional resume formats such as Microsoft Word (.docx).
