from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime

from app.db.session import SessionLocal
from app.market_calendar import NonTradingSessionError, ScanNotDueError
from app.market_data.provider import get_market_data_provider
from app.services.daily_reports import (
    DailyReportGenerationError,
    DailyScanAlreadyRunningError,
    generate_daily_top10_report,
)
from app.services.stock_analysis import get_stock_ai_service

logger = logging.getLogger(__name__)


async def run_daily_top10_scan(moment: datetime | None = None) -> dict[str, object]:
    with SessionLocal() as db:
        try:
            result = await generate_daily_top10_report(
                db,
                provider=get_market_data_provider(),
                ai_service=get_stock_ai_service(),
                moment=moment or datetime.now(UTC),
            )
        except ScanNotDueError as exc:
            db.rollback()
            return {"status": "skipped", "reason": "before_scan_time", "detail": str(exc)}
        except NonTradingSessionError as exc:
            db.rollback()
            return {"status": "skipped", "reason": "non_trading_session", "detail": str(exc)}
        except DailyScanAlreadyRunningError as exc:
            db.rollback()
            return {"status": "skipped", "reason": "already_running", "detail": str(exc)}
        except DailyReportGenerationError:
            db.rollback()
            logger.exception("Daily top-ten report generation failed")
            raise

    payload = {
        "status": "created" if result.created else "already_exists",
        "report_id": str(result.report.id),
        "scan_run_id": str(result.scan_run.id),
        "source_session_date": result.report.source_snapshot.get(
            "source_session_date"
        ),
        "target_session_date": result.report.target_session_date.isoformat(),
        "generated_at": (
            result.report.generated_at.isoformat()
            if result.report.generated_at is not None
            else None
        ),
    }
    logger.info("Daily top-ten scan result: %s", payload)
    return payload


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(asyncio.run(run_daily_top10_scan()), ensure_ascii=False))


if __name__ == "__main__":
    main()
