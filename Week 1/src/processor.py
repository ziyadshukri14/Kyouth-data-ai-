from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError
from urllib.parse import urlparse
import json


# Pydantic Model
class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


# Helper: clean text
def clean(text: str) -> str:
    return " ".join(text.split()) if text else ""


# Main Processor
def process_all_html(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    print("🥈 Silver:...\n")

    output_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print("⚠️ Input directory does not exist")
        print("\n📊 Silver Summary:")
        print("Total: 0 | Processed: 0 | Skipped: 0")
        return

    files = list(input_path.glob("*.html"))

    total = len(files)
    processed = 0
    skipped = 0

    for file_path in files:
        try:
            html = file_path.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")

            # Extract source_id safely
            source_id = ""

            meta = soup.find("meta", property="og:url")
            if meta and meta.get("content"):
                url = meta["content"]
                parsed = urlparse(url)
                parts = parsed.path.strip("/").split("/")
                source_id = parts[-1] if parts else ""

            # Important fix: skip if no source_id
            if not source_id:
                print(f"⚠️ Missing source_id in: {file_path.name}")
                skipped += 1
                continue

            # Extract fields
            job_title_tag = soup.find(attrs={"data-automation": "job-detail-title"})
            company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
            desc_tag = soup.find(attrs={"data-automation": "jobAdDetails"})

            job_title = clean(job_title_tag.get_text(" ", strip=True) if job_title_tag else "")
            company = clean(company_tag.get_text(" ", strip=True) if company_tag else "")
            description = clean(desc_tag.get_text(" ", strip=True) if desc_tag else "")

            # Missing field check
            missing = []
            if not job_title:
                missing.append("job_title")
            if not company:
                missing.append("company")
            if not description:
                missing.append("description")

            if missing:
                print(f"⚠️ Missing {', '.join(missing)} in: {file_path.name}")
                skipped += 1
                continue

            # Validate
            job = JobListing(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description
            )

            # Save JSON
            output_file = output_path / f"{source_id}.json"

            output_file.write_text(
                json.dumps(job.model_dump(), indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            print(f"✅ Processed: {file_path.name}")
            processed += 1

        except ValidationError:
            print(f"⚠️ Validation error in: {file_path.name}")
            skipped += 1

        except Exception:
            print(f"❌ Failed: {file_path.name}")
            skipped += 1

    # Summary
    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")