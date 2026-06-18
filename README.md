# K-Youth Data Pipeline Project

## Project Description

This project is a Python-based ETL (Extract, Transform, Load) data pipeline built using Medallion Architecture.  
The purpose of this project is to process raw job listing data from `.mhtml` files, clean and transform the data into structured JSON format, store the processed data inside a SQLite database, and perform data quality profiling.

The pipeline is divided into four layers:

- Bronze Layer → Extract raw `.mhtml` into `.html`
- Silver Layer → Clean and structure HTML into JSON
- Gold Layer → Store structured data inside SQLite database
- Profiling Layer → Check data quality and validate records

The project simulates how modern data engineering pipelines work in real-world industry systems.

---

# Setup Instructions

## Prerequisites

Install the following before running the project.

### Python Version

Project uses:

```bash
Python 3.14
```

Check version:

```bash
python --version
```

---

## Install UV Package Manager

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Check installation:

```bash
uv --version
```

---

## Install Dependencies

Install required libraries:

```bash
uv add beautifulsoup4
uv add pydantic
```

or

```bash
uv pip install beautifulsoup4 pydantic
```

---

## Project Structure

```text
project/
│
├── data/
│   ├── 0_source/
│   ├── 1_bronze/
│   ├── 2_silver/
│   └── 3_gold/
│
├── src/
│   ├── ingestor.py
│   ├── processor.py
│   ├── loader.py
│   └── profiler.py
│
├── main.py
└── README.md
```

---

# Usage

Run the pipeline using command line.

## 1. Bronze Layer (Extract MHTML)

Command:

```bash
uv run python main.py ingest
```

Output example:

```bash
🥉 Bronze:...
✅ Extracted: file1.mhtml
✅ Extracted: file2.mhtml

📊 Bronze Summary:
Total: 100 | Extracted: 100 | Failed: 0
```

---

## 2. Silver Layer (Process HTML)

Command:

```bash
uv run python main.py process
```

Output example:

```bash
🥈 Silver:...
✅ Processed: file1.html
⚠️ Missing description in: file2.html

📊 Silver Summary:
Total: 100 | Processed: 84 | Skipped: 16
```

---

## 3. Gold Layer (Load Database)

Command:

```bash
uv run python main.py load
```

Output example:

```bash
🥇 Gold:...
✅ Inserted: file1.json
⏭️ Skipped (duplicate): file2.json

📊 Gold Summary:
Total: 84 | Inserted: 84 | Skipped: 0
```

---

## 4. Data Profiling

Command:

```bash
uv run python main.py profile
```

Output example:

```bash
--- 🔍 DATA QUALITY REPORT ---

📈 Total Records: 84

❓ Missing Values
job_title: 0
company: 0
description: 0

📝 Avg Description Length: 2654 chars

⚠️ Shortest Description: 32 chars
source_id: 91647393 | job_title: Software Engineer

🚨 Longest Description: 6781 chars
source_id: 91731564 | job_title: Automation Engineer
```

---

## 5. Run Full Pipeline

Command:

```bash
uv run python main.py all
```

Runs:

```text
ingest → process → load → profile
```

---

# Technical Reflections

## Day 1: The Extractor (Medallion & Lakehouses)

Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?

**Answer:**

Keeping the raw HTML files is important because it preserves the original source data before any transformation happens. If errors happen during processing, developers can go back to the original files and reprocess the data again without needing to collect the source data another time.

It also makes debugging easier because we can compare raw data with processed data to identify where the issue happened during extraction or transformation.

---

## Day 2: Treatment Plant (ETL vs ELT & Scale)

Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?

**Answer:**

Cloud systems prefer ELT because raw data can be stored immediately and transformed later when needed. This allows companies to keep all original data and apply different transformations in the future without collecting data again.

Processing files sequentially means files are handled one by one, which becomes slow when handling large datasets. Distributed processing solves this by splitting the workload across multiple machines so many files can be processed at the same time.

---

## Day 3: The Blueprint & The Vault (Storage & Contracts)

What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting nulls into DB? How does `INSERT OR IGNORE` help prevent duplicate records?

**Answer:**

If an important field like `job_title` is missing, the system should stop processing that record and reject it. Failing early helps detect bad or incomplete data before it enters the database.

If null values are inserted silently, dashboards and reports may become inaccurate. `INSERT OR IGNORE` helps prevent duplicate records by checking the primary key before inserting, so running the pipeline multiple times will not create duplicate data.

---

## Day 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?

**Answer:**

If `processor.py` crashes halfway, the pipeline stops and some files may remain unprocessed. This creates incomplete data and requires manual rerunning.

Automated orchestration tools such as Apache Airflow are more reliable because they automatically retry failed tasks, manage dependencies between tasks, and schedule jobs without requiring manual intervention. This reduces human error and improves pipeline reliability in production systems.

---

# Final Architecture Flow

```text
0_source (.mhtml files)
        ↓
1_bronze (.html extracted)
        ↓
2_silver (.json cleaned data)
        ↓
3_gold (SQLite jobs.db)
        ↓
Data Profiling / QA Report
```

Pipeline Command Flow:

```text
main.py
   ├── ingest
   ├── process
   ├── load
   ├── profile
   └── all
```
