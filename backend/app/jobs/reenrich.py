import logging

from app.db.session import SessionLocal
from app.models import MarketReport
from app.services.report_selection import enrich_daily_report_selection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    with SessionLocal() as db:
        reports = (
            db.query(MarketReport)
            .order_by(MarketReport.target_session_date.desc())
            .limit(5)
            .all()
        )
        for r in reports:
            logger.info(
                "Re-enriching report: %s for target date: %s",
                r.id,
                r.target_session_date,
            )
            enrich_daily_report_selection(db, report_id=r.id)
        db.commit()
    logger.info("Completed successfully!")


if __name__ == "__main__":
    main()
