import sys
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile


def main():

    # ETL folder structure
    input_raw = "data/0_source"
    bronze = "data/1_bronze"
    silver = "data/2_silver"
    gold = "data/3_gold"      # FIXED → folder only

    # No command provided
    if len(sys.argv) < 2:
        print("Usage: python main.py [ingest|process|load|profile|full]")
        return

    command = sys.argv[1]

    match command:

        # DAY 1
        case "ingest":
            print("week_1 python main.py ingest")
            ingest_all_mhtml(input_raw, bronze)

        # DAY 2
        case "process":
            print("week_1 python main.py process")
            process_all_html(bronze, silver)

        # DAY 3
        case "load":
            print("week_1 python main.py load")
            load_all_jsons(silver, gold)

        # DAY 4
        case "profile":
            print("week_1 python main.py profile")
            run_data_profile("data/3_gold/jobs.db")

        # FULL PIPELINE
        case "all":
            print("week_1 full pipeline start")

            ingest_all_mhtml(input_raw, bronze)
            process_all_html(bronze, silver)
            load_all_jsons(silver, gold)
            run_data_profile("data/3_gold/jobs.db")

        case _:
            print("Unknown command")
            print("Usage: python main.py [ingest|process|load|profile|full]")


if __name__ == "__main__":
    main()