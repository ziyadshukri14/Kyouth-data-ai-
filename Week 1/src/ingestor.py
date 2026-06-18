from pathlib import Path
import email
import quopri


def ingest_all_mhtml(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    print("🥉 Bronze:...\n")

    # Check input folder exists
    if not input_path.exists():
        print(f"⚠️ Input directory does not exist: {input_dir}")
        print("\n📊 Bronze Summary:")
        print("Total: 0 | Extracted: 0 | Failed: 0")
        return

    # Create output folder if missing
    output_path.mkdir(parents=True, exist_ok=True)

    # Get all mhtml files
    files = list(input_path.glob("*.mhtml"))

    if not files:
        print(f"⚠️ No MHTML files found in: {input_dir}")
        print("\n📊 Bronze Summary:")
        print("Total: 0 | Extracted: 0 | Failed: 0")
        return

    total = len(files)
    extracted = 0
    failed = 0

    # Process each file
    for file_path in files:
        try:
            raw_data = file_path.read_bytes()
            msg = email.message_from_bytes(raw_data)

            html_content = None

            # find text/html part
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload()

                    # handle quoted-printable safely
                    if isinstance(payload, str):
                        html_content = quopri.decodestring(payload.encode("utf-8", errors="ignore"))
                        html_content = html_content.decode("utf-8", errors="ignore")
                    else:
                        html_content = payload.decode("utf-8", errors="ignore")

                    break

            # if no html found
            if not html_content:
                print(f"⚠️ No HTML content found in: {file_path.name}")
                failed += 1
                continue

            # save html
            output_file = output_path / f"{file_path.stem}.html"
            output_file.write_text(html_content, encoding="utf-8")

            print(f"✅ Extracted: {file_path.name}")
            extracted += 1

        except Exception:
            print(f"❌ Failed: {file_path.name}")
            failed += 1

    # Summary
    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")