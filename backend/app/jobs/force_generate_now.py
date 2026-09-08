import asyncio
import json
import logging

from app.jobs.generate_daily_top10 import run_daily_top10_scan


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    res = asyncio.run(run_daily_top10_scan(force_regenerate=True))
    print("FORCE_REGEN_RESULT:", json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
