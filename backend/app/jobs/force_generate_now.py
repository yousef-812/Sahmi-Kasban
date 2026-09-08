import asyncio
import json
import logging

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.jobs.generate_daily_top10 import run_daily_top10_scan
from app.models import MarketReport, MarketReportItem


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as db:
        latest = db.scalars(
            select(MarketReport).order_by(MarketReport.created_at.desc()).limit(1)
        ).first()
        if latest:
            print(f"Deleting latest report {latest.id} for target {latest.target_session_date}")
            db.execute(delete(MarketReportItem).where(MarketReportItem.report_id == latest.id))
            db.delete(latest)
            db.commit()
        else:
            print("No previous report found to delete")

    res = asyncio.run(run_daily_top10_scan())
    print("FORCE_REGEN_RESULT:", json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
