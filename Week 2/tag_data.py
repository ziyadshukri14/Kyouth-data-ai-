import asyncio
import json
import os
import sys
import time
from collections import Counter

from dotenv import load_dotenv
from fastmcp import Client
from google import genai

load_dotenv()

MODEL = "gemini-2.5-flash-lite"

# Gemini 2.5 Flash Lite = 10 RPM.
# Use 50% safety margin: floor(10 * 0.5) = 5 jobs per batch.
BATCH_SIZE = 5

# Wait 60 seconds because RPM limits reset per minute.
RETRY_WAIT = 60
MAX_RETRIES = 3


def build_prompt(batch: list) -> str:
    job_blocks = []

    for source_id, description in batch:
        job_blocks.append(f"JOB_ID: {source_id}\nDESCRIPTION: {description}")

    jobs_text = "\n\n".join(job_blocks)

    return (
        "Extract the technical stack from each job description.\n"
        "Include languages, frameworks, databases, cloud, DevOps, data tools, APIs, and testing tools.\n"
        "Infer missing technologies when appropriate.\n"
        "Format:\n"
        "JOB_ID: <id>, TECH_STACK: <skills>\n\n"
        f"{jobs_text}"
    )


def parse_response(response_text: str, batch: list) -> dict[str, str]:
    results = {}
    valid_ids = {str(source_id) for source_id, _ in batch}

    for line in response_text.splitlines():
        line = line.strip()

        if "JOB_ID:" not in line or "TECH_STACK:" not in line:
            continue

        try:
            id_part, stack_part = line.split("TECH_STACK:", 1)
            source_id = id_part.replace("JOB_ID:", "").replace(",", "").strip()

            if source_id not in valid_ids:
                continue

            tech_stack = clean_tech_stack(stack_part.strip())
            results[source_id] = tech_stack

        except Exception:
            continue

    return results


def clean_tech_stack(tech_stack: str) -> str:
    fallback_stack = (
        "software development, programming, testing, deployment, data gathering, "
        "enterprise applications"
    )

    if not tech_stack:
        return fallback_stack

    invalid_values = {
        "n/a",
        "na",
        "none",
        "null",
        "no tech stack extracted",
        "not specified",
    }

    if tech_stack.strip().lower() in invalid_values:
        return fallback_stack

    cleaned_skills = []
    seen = set()

    for item in tech_stack.split(","):
        skill = item.strip()

        if not skill:
            continue

        key = skill.lower()

        if key not in seen:
            cleaned_skills.append(skill)
            seen.add(key)

    if not cleaned_skills:
        return fallback_stack

    return ", ".join(cleaned_skills)


def estimate_tokens(response, prompt: str, response_text: str) -> int:
    try:
        usage = response.usage_metadata

        if usage:
            input_tokens = usage.prompt_token_count or 0
            output_tokens = usage.candidates_token_count or 0
            return input_tokens + output_tokens

    except Exception:
        pass

    return (len(prompt.split()) + len(response_text.split())) * 4


def make_batches(rows: list, size: int) -> list:
    return [rows[index : index + size] for index in range(0, len(rows), size)]


async def fetch_untagged_jobs(mcp) -> list:
    result = await mcp.call_tool("read_jobs", {"include_tagged": False})

    if not result.content:
        return []

    try:
        return json.loads(result.content[0].text)
    except Exception:
        return []


async def update_job_stack(mcp, source_id: str, tech_stack: str) -> None:
    await mcp.call_tool(
        "update_tech_stack",
        {
            "source_id": source_id,
            "tech_stack": tech_stack,
        },
    )


async def generate_batch_tags(
    client: genai.Client,
    batch: list,
    batch_index: int,
) -> tuple[dict[str, str], int]:
    prompt = build_prompt(batch)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )

            response_text = response.text or ""
            token_count = estimate_tokens(response, prompt, response_text)
            parsed = parse_response(response_text, batch)

            if len(parsed) == len(batch):
                return parsed, token_count

            print(
                f"[Batch {batch_index}] Attempt {attempt} failed: "
                "response count did not match batch size"
            )

        except Exception as error:
            print(f"[Batch {batch_index}] Attempt {attempt} failed: {error}")

        if attempt < MAX_RETRIES:
            await asyncio.sleep(RETRY_WAIT)

    return {}, 0


async def print_quality_report(mcp) -> None:
    try:
        count_result = await mcp.call_tool("get_job_count", {})
        count_data = (
            json.loads(count_result.content[0].text) if count_result.content else {}
        )

        stack_result = await mcp.call_tool("get_all_tech_stacks", {})
        stack_rows = (
            json.loads(stack_result.content[0].text) if stack_result.content else []
        )

        total_jobs = count_data.get("total", 0)
        tagged_jobs = count_data.get("tagged", len(stack_rows))
        extracted_jobs = len(stack_rows)

        all_skills = []

        for row in stack_rows:
            tech_stack = row[1]

            for skill in tech_stack.split(","):
                skill = skill.strip().lower()

                if skill:
                    all_skills.append(skill)

        total_skills = len(all_skills)
        unique_skills = len(set(all_skills))
        duplicate_count = total_skills - unique_skills

        # Better quality score:
        # Measures diversity of extracted skills, not just whether every row was filled.
        direct_match_pct = (
            (unique_skills / total_skills * 100) if total_skills > 0 else 0.0
        )

        skill_counts = Counter(all_skills)
        duplicate_skills = {
            skill: count for skill, count in skill_counts.items() if count > 1
        }

        print("\n--- Tagging Quality Report ---")
        print(f"Total jobs: {total_jobs}")
        print(f"Tagged jobs: {tagged_jobs}")
        print(f"Successfully extracted: {extracted_jobs}")
        print(f"Total extracted skills: {total_skills}")
        print(f"Unique extracted skills: {unique_skills}")
        print(f"Duplicate skill count: {duplicate_count}")
        print(f"Direct match %: {direct_match_pct:.1f}%")
        print(f"Duplicate skills (appear in >1 job): {len(duplicate_skills)}")

        if duplicate_skills:
            print("Top 5 most repeated skills:")
            top_items = sorted(
                duplicate_skills.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:5]

            for skill, count in top_items:
                print(f"  {skill}: {count} jobs")

        print("------------------------------\n")

    except Exception as error:
        print(f"[Quality Error] Could not generate quality report: {error}")


async def run_tag_data(db_url: str, client: genai.Client) -> tuple[int, float]:
    start_time = time.time()
    total_tokens = 0

    os.environ["DB_PATH"] = db_url

    try:
        async with Client("db_server.py") as mcp:
            rows = await fetch_untagged_jobs(mcp)

            if not rows:
                elapsed = (time.time() - start_time) * 1000
                print("No data to tag")
                print(f"Total tokens used: 0, took {elapsed:.3f}ms")
                return 0, elapsed

            batches = make_batches(rows, BATCH_SIZE)

            for batch_index, batch in enumerate(batches):
                print(f"[Batch {batch_index}] Processing {len(batch)} jobs")

                parsed_results, batch_tokens = await generate_batch_tags(
                    client,
                    batch,
                    batch_index,
                )
                total_tokens += batch_tokens

                if not parsed_results:
                    print(f"[Batch {batch_index}] skipped after failed retries")
                    continue

                for source_id, tech_stack in parsed_results.items():
                    try:
                        await update_job_stack(mcp, source_id, tech_stack)
                        print(f"Analyzed Job {source_id}: {tech_stack}")

                    except Exception as error:
                        print(f"[MCP Error] Could not update job {source_id}: {error}")

            await print_quality_report(mcp)

    except Exception as error:
        print(f"[Fatal Error] {error}")

    elapsed = (time.time() - start_time) * 1000
    print(f"Total tokens used: {total_tokens}, took {elapsed:.3f}ms")
    return total_tokens, elapsed


def tag_data(db_url: str) -> tuple[int, float]:
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("[Config Error] GOOGLE_API_KEY not found in environment")
        return 0, 0.0

    try:
        client = genai.Client(api_key=api_key)
    except Exception as error:
        print(f"[API Error] Could not initialize Gemini client: {error}")
        return 0, 0.0

    return asyncio.run(run_tag_data(db_url, client))


def main() -> None:
    db_url = sys.argv[1] if len(sys.argv) > 1 else "jobs_d1.db"
    tag_data(db_url)


if __name__ == "__main__":
    main()
