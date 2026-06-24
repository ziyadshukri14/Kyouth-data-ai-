# Project Overview

This project was developed as part of the K-Youth Data AI Program Week 2 assignment. The objective is to build an AI-powered workflow that enriches job market data and identifies technical skill gaps between a candidate's resume and industry requirements.

The project uses Google Gemini models, SQLite databases, and FastMCP to create an automated pipeline for job analysis and resume evaluation. The solution combines data tagging, prompt engineering, token optimization, batching strategies, and skill matching techniques to support career development and job readiness analysis.

The project consists of three main components:

### Day 0 – Environment and Model Setup

This stage prepares the development environment using Python, uv, SQLite, FastMCP, and Google Gemini. A unified model interface is implemented to interact with Gemini models while handling API configuration and rate limits.

### Day 1–2 – Job Data Tagging

The system reads job descriptions stored in a SQLite database and extracts relevant technical skills from each job posting. Extracted technologies are stored in the `tech_stack` column to create a structured representation of market skill requirements. Batch processing, retry mechanisms, token tracking, and quality reporting are implemented to improve efficiency and reliability.

### Day 3–4 – Resume Skill Gap Analysis

The system analyzes a candidate's resume and compares the extracted skills against the skills required by jobs in the database. Missing skills are identified deterministically and returned in a structured Pydantic model. The solution includes prompt hardening, jailbreak protection, token measurement, demand analysis, and MCP integration for database access.

Overall, this project demonstrates practical applications of Large Language Models (LLMs) for data enrichment, skill extraction, and career gap analysis while emphasizing reliability, scalability, and efficient API usage.

# Setup Instructions

## Prerequisites

Before running this project, ensure the following software is installed:

- Python 3.14
- uv package manager
- Ollama 0.21.\* with the following models installed: llama3.1, phi3, deepseek-r1:1.5b
- Google Gemini API Key

Verify installation:

```bash
python --version
uv --version
git --version
```

---

## 1. Clone the Repository

```bash
cd "Week 2"
```

---

## 2. Create Virtual Environment

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

Install all project dependencies:

```bash
uv sync
```

Alternatively:

```bash
uv add fastmcp==3.4.2
uv add google-genai==2.9.0
uv add ollama==0.6.2
uv add pydantic==2.13.4
uv add python-dotenv==1.2.2
uv add ruff==0.15.17
```

---

## 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following configuration:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Replace `your_gemini_api_key_here` with a valid Google Gemini API key.

**Important:** Never commit API keys or secrets to version control.

---

## 6. Project Structure

```text
Week 2/
├── db_server.py
├── find_skill_gaps.py
├── jobs_d1.db
├── prompt_model.py
├── rate_limits.txt
├── resume_d3.txt
├── tag_data.py
├── README.md
├── pyproject.toml
├── uv.lock
└── .env
```

---

## 7. Running the Project

### Tag Job Descriptions

Populate the `tech_stack` column in the jobs database:

```bash
uv run tag_data.py jobs_d1.db
```

Example output:

```text
Analyzed Job 91397216: SQL, Python, R, Excel, Tableau, PowerBI, DataStudio
Analyzed Job 91347112: Java, Spring Framework, Spring Boot, Python
```

---

### Run Skill Gap Analysis

Compare a resume against the tagged jobs database:

```bash
uv run find_skill_gaps.py resume_d3.txt jobs_d1.db
```

Example output:

```text
gaps=['alibaba cloud', 'api', 'aws', 'azure]
top_missing_skills=['aws', 'docker']
time=1833.917
tokens=192
```

---

## Troubleshooting

### Gemini Rate Limit Exceeded

Example:

```text
429 RESOURCE_EXHAUSTED
```

Solution:

- Wait for the quota reset.
- Switch to another Gemini model if available.
- Reduce unnecessary test executions.

### Gemini Service Unavailable

Example:

```text
503 UNAVAILABLE
```

Solution:

- Retry after a short delay.
- The application automatically retries failed requests.

### Database Not Found

Ensure the database file exists:

```bash
ls jobs_d1.db
```

and verify the correct file path is supplied when running the program.

# Usage

Run all commands from inside the `Week 2/` folder.

---

## 1. Test Gemini Connection

Verify that your API key and Gemini client are working correctly.

```bash
uv run prompt_model.py gemini-2.5-flash "Hello"
```

Expected output:

```text

--- RESPONSE ---

Hi there! How can I help you today?
```

Possible error:

```text
--- RESPONSE ---

[Gemini Error] Missing GOOGLE_API_KEY in environment
```

---

## 2. Tag Job Descriptions

This command reads job descriptions from the SQLite database and populates the `tech_stack` column using Gemini.

```bash
uv run tag_data.py jobs_d1.db
```

Expected output:

```text
[Batch 0] Processing 5 jobs

Analyzed Job 91397216: SQL, Python, R, Tableau
Analyzed Job 91347112: Java, Spring Framework, Spring Boot
Analyzed Job 91597624: Python, SQL, API, Power BI

--- Tagging Quality Report ---
Total jobs: 7
Tagged jobs: 7
Successfully extracted: 76
Direct match %: 75.0%
Duplicate skills (appear in >1 job): 9

Top 5 most repeated skills:
  python: 6 jobs
  sql: 4 jobs
  aws: 3 jobs
  docker: 3 jobs
  postgresql: 3 jobs

Total tokens used: 3216, took 68650.890ms
```

If all rows have already been tagged:

```text
No data to tag
Total tokens used: 0, took 568.765ms
```

---

## 3. Find Skill Gaps

This command compares a resume against the skills required in the tagged jobs database.

```bash
uv run find_skill_gaps.py resume_d3.txt jobs_d1.db
```

Expected output:

```text
gaps=['alibaba cloud', 'api', 'aws', 'azure]

top_missing_skills=[
    'aws',
    'docker',
    'gcp',
    'sql'
]

time=1833.917
tokens=192
```

The output contains:

- **gaps** → Skills missing from the resume.
- **top_missing_skills** → Most demanded missing skills based on job market demand.
- **tokens** → Total Gemini tokens consumed.
- **time** → Execution time in milliseconds.

---

## 4. Database Validation

Check whether job records have been tagged successfully.

Open SQLite:

```bash
sqlite3 jobs_d1.db
```

View tagged results:

```sql
SELECT source_id, tech_stack
FROM jobs
LIMIT 10;
```

Example output:

```text
91397216|SQL, Python, R, Excel
91347112|Java, Spring Framework, Spring Boot
91597624|Python, SQL, API, Power BI
```

Exit SQLite:

```sql
.quit
```

---

## Common Errors

### Gemini Rate Limit

```text
429 RESOURCE_EXHAUSTED
```

Cause:

- Daily Gemini free-tier quota exceeded.

Solution:

- Wait for quota reset.
- Switch to another Gemini model.

---

## API / Function Reference

### tag_data.py

#### tag_data(db_url: str) -> tuple[int, float]

Reads all rows from the `jobs` table where `tech_stack` is NULL or empty, sends them in batches to Gemini for tech stack extraction, and writes the results back to the database through MCP.

- Model: `gemini-2.5-flash-lite`
- Batch size: `5` — uses a 50% safety margin from the 10 RPM free-tier limit.
- Retry wait: `60 seconds` — allows the rate-limit window to reset before retrying.
- Max retries: `3` — prevents infinite retries on persistent failures.
- Database access: via MCP server (`db_server.py`)
- Returns: `(total_tokens, elapsed_ms)`

Also prints a tagging quality report showing:

- Total jobs
- Tagged jobs
- Successfully extracted jobs
- Total extracted skills
- Unique extracted skills
- Direct match %
- Duplicate skill count
- Top repeated skills

---

### find_skill_gaps.py

#### find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult

Reads a resume text file and a tagged jobs database, extracts skills from both, and returns the gaps: skills present in the job market but missing from the resume.

- Model: `gemini-2.5-flash-lite`
- `temperature=0` and `seed=42` for deterministic resume skill extraction
- Skills separated by `/` are split into individual skills, except `a/b testing` and `ci/cd`
- All gaps are sorted and converted to lowercase
- Database access: via MCP server (`db_server.py`)
- Resume input is sanitized against prompt injection before being sent to Gemini
- Returns a `SkillGapResult` Pydantic model

#### SkillGapResult fields

| Field              | Type      | Description                                      |
| ------------------ | --------- | ------------------------------------------------ |
| gaps               | List[str] | Sorted lowercase list of missing skills          |
| top_missing_skills | List[str] | Top 5 most in-demand missing skills by job count |
| tokens             | int       | Total tokens used                                |
| time               | float     | Elapsed time in milliseconds                     |

### db_server.py

MCP server that abstracts all SQLite database access. Exposes four tools:

| Tool                | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| read_jobs           | Returns untagged jobs (or all jobs if `include_tagged=True`) |
| update_tech_stack   | Updates the `tech_stack` column for a specific job           |
| get_all_tech_stacks | Returns all valid non-empty tech stacks                      |
| get_job_count       | Returns total jobs and tagged job counts                     |

### prompt_model.py

#### prompt_model(model: str, prompt: str) -> str

Acts as a model router that sends prompts to either Google Gemini or a local Ollama model depending on the model name provided. Returns the generated response as a string.

All API and model errors are handled gracefully and returned as error messages instead of crashing the program.

**Supported Gemini Models**

- gemini-2.5-flash
- gemini-2.5-flash-lite
- gemini-3-flash-preview

**Supported Ollama Models**

- llama3.1
- phi3
- deepseek-r1:1.5b
- Any other Ollama model installed locally

**Input**

| Parameter | Type | Description                        |
| --------- | ---- | ---------------------------------- |
| model     | str  | Name of the Gemini or Ollama model |
| prompt    | str  | User prompt to send to the model   |

**Output**

| Return Type | Description                     |
| ----------- | ------------------------------- |
| str         | Model response or error message |

**Related Functions**

| Function       | Purpose                                             |
| -------------- | --------------------------------------------------- |
| is_gemini()    | Checks whether the selected model is a Gemini model |
| call_gemini()  | Sends prompts to Google Gemini                      |
| call_ollama()  | Sends prompts to a local Ollama model               |
| prompt_model() | Routes requests to the correct backend model        |

## Data / Assumptions

### Assumptions

- The SQLite database contains a `jobs` table.
- Each job record includes:
  - `source_id`
  - `description`
  - `tech_stack`

- Resume files are provided in plain text (`.txt`) format.
- The `tech_stack` field is generated by `tag_data.py`.
- Technical skills are stored as comma-separated values.
- Resume skills and job skills are normalized before comparison.
- Non-technical information such as personal details, certifications, and soft skills are ignored during skill extraction.
- Database operations are performed through MCP (`db_server.py`) instead of direct SQL access.

### Data Flow

```text
Resume (.txt)
      │
      ▼
Gemini Skill Extraction
      │
      ▼
Resume Skills
      │
      │
      ├─────────────── Compare ───────────────┐
      │                                       │
      ▼                                       ▼

Jobs Database (jobs_d1.db)
      │
      ▼
MCP Server (db_server.py)
      │
      ▼
tech_stack Values
      │
      ▼
Database Skills
      │
      ▼

Missing Skills = Database Skills - Resume Skills
```

## Testing

### Skill Gap Analysis Test

The skill gap analysis function was tested using the provided resume and jobs database.

**Command**

```bash
uv run find_skill_gaps.py resume_d3.txt jobs_d1.db
```

**Verification**

- Confirmed that all returned gaps exist in the job database.
- Confirmed that skills already present in the resume do not appear in the gap list.
- Verified that the top missing skills are ranked according to job demand frequency.

---

### Deterministic Output Test

The program was executed multiple times using the same resume and database.

**Example**

```text
Run 1:
gaps=['alibaba cloud', 'api', 'aws', 'azure', ...]
tokens=206

Run 2:
gaps=['alibaba cloud', 'api', 'aws', 'azure', ...]
tokens=206
```

The output remained identical across repeated executions.

---

### MCP Database Validation

The MCP server was tested by:

1. Reading untagged jobs using `read_jobs`.
2. Updating records using `update_tech_stack`.
3. Retrieving stored skills using `get_all_tech_stacks`.
4. Verifying counts using `get_job_count`.

This confirmed that all database operations function correctly through MCP.

---

**Validation**

- Suspicious phrases were removed by `sanitize_resume()`.
- Gemini continued extracting legitimate technical skills.
- No fake skills appeared in the final results.

---

### Error Handling Test

The system was tested under different failure scenarios:

| Scenario                   | Expected Result                 |
| -------------------------- | ------------------------------- |
| Missing API key            | Configuration error displayed   |
| Invalid resume path        | File error displayed            |
| Gemini rate limit exceeded | Error handled gracefully        |
| Empty database             | No crash, empty result returned |

These tests verified that the application handles failures without crashing.

## Prompt Optimization

The prompt used in `tag_data.py` was optimized to reduce token usage while still producing accurate tech stack extraction results.

### Baseline Prompt (Verbose)

```text
Extract the technical stack from each job description.
Include programming languages, frameworks, libraries, databases,
cloud platforms, DevOps tools, data tools, APIs, testing tools,
and technical methods.

If technologies are not explicitly mentioned,
infer reasonable technical skills from the job responsibilities.

Return only technical skills as a comma-separated list.

Return one line per job in this format:
JOB_ID: <id>, TECH_STACK: <skills>

{jobs_text}
```

### Optimized Prompt (Concise)

```text
Extract the technical stack from each job description.
Include languages, frameworks, databases, cloud, DevOps,
data tools, APIs, and testing tools.
Infer missing technologies when appropriate.

Format:
JOB_ID: <id>, TECH_STACK: <skills>

{jobs_text}
```

### Results

| Version | Prompt Style | Token Usage | Output Quality |
| ------- | ------------ | ----------- | -------------- |
| 1       | Baseline     | Higher      | Correct        |
| 2       | Optimized    | Lower       | Correct        |

### Impact

- Reduced prompt length by removing unnecessary instructions.
- Lower token consumption per batch request.
- Maintained the same output format required by the parser.
- No noticeable reduction in extracted tech stack quality.

The optimized prompt improves efficiency while preserving consistent tagging results.

## Limitations

- The Gemini free tier has request limits, so processing a large number of job records may quickly consume the available daily quota.
- During periods of high usage, Gemini may temporarily return service unavailable (503) errors. Retry logic is implemented, but successful recovery is not guaranteed.
- The system currently supports resume files in plain text (`.txt`) format only.
- Skill comparison is based on normalized string matching. Similar skills with different naming conventions (e.g., `node.js` and `nodejs`) may be treated as separate skills.
- Job records that do not produce a meaningful technical stack are assigned a fallback value and are not considered during skill gap analysis.

## Architecture Reflection

### Design Choices

LLMs are used to extract technical skills from job descriptions and resumes, where traditional rules would be difficult to apply. All other processing, such as skill comparison, sorting, and gap detection, is handled using Python. Database operations are separated into `db_server.py` using MCP, making the code easier to maintain.

### Trade-offs

Using `temperature=0` and `seed=42` helps produce consistent results across multiple runs. Batch processing in `tag_data.py` reduces API usage and helps stay within Gemini rate limits, although processing large datasets may take longer.

### Future Improvements

Possible enhancements include:

- Support for PDF resumes
- Better skill matching for similar terms (e.g., `node.js` and `nodejs`)
- Caching results to reduce repeated API calls
- Adding automated test cases for validation and regression test
