import asyncio
import json
import logging
from datetime import UTC, datetime

from app.jobs.generate_daily_top10 import run_daily_top10_scan


def main():
    logging.basicConfig(level=logging.INFO)
    # Force run for July 30, 2026 (a valid EGX trading day)
    moment = datetime(2026, 7, 30, 18, 0, 0, tzinfo=UTC)
    res = asyncio.run(run_daily_top10_scan(moment))
    print("Execution Result:")
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
