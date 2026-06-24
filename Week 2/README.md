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
