from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.db.session import SessionLocal
from app.market_calendar import NonTradingSessionError, ScanNotDueError
from app.market_data.catalog import ensure_market_instrument_catalog
from app.market_data.egx_symbols import EGX_SEED_SYMBOLS
from app.market_data.provider import get_market_data_provider
from app.models import MarketInstrumentCatalog, User
from app.services.daily_reports import (
    DailyReportGenerationError,
    DailyScanAlreadyRunningError,
    generate_daily_top10_report,
)
from app.services.notifications import create_notification
from app.services.stock_analysis import get_stock_ai_service

logger = logging.getLogger(__name__)


def _active_market_tickers(db) -> tuple[str, ...]:
    tickers = tuple(
        db.scalars(
            select(MarketInstrumentCatalog.ticker)
            .where(MarketInstrumentCatalog.active.is_(True))
            .order_by(MarketInstrumentCatalog.ticker)
        ).all()
    )
    return tickers or EGX_SEED_SYMBOLS


def _notify_report_ready(db, *, report_id: str, target_session_date: str) -> int:
    user_ids = db.scalars(
        select(User.id).where(
            User.status == "active",
            User.email_verified.is_(True),
        )
    ).all()
    for user_id in user_ids:
        create_notification(
            db,
            user_id=user_id,
            title="تقرير أفضل 10 جاهز",
            body="اكتمل تحليل السوق وأصبح تقرير الجلسة القادمة متاحًا داخل التطبيق.",
            category="market_report",
            data={
                "report_id": report_id,
                "target_session_date": target_session_date,
            },
        )
    db.commit()
    return len(user_ids)


async def run_daily_top10_scan(moment: datetime | None = None) -> dict[str, object]:
    with SessionLocal() as db:
        try:
            await ensure_market_instrument_catalog(db)
            tickers = _active_market_tickers(db)
            result = await generate_daily_top10_report(
                db,
                provider=get_market_data_provider(),
                ai_service=get_stock_ai_service(),
                moment=moment or datetime.now(UTC),
                tickers=tickers,
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

        notified_users = 0
        if result.created:
            notified_users = _notify_report_ready(
                db,
                report_id=str(result.report.id),
                target_session_date=result.report.target_session_date.isoformat(),
            )

    payload = {
        "status": "created" if result.created else "already_exists",
        "report_id": str(result.report.id),
        "scan_run_id": str(result.scan_run.id),
        "source_session_date": result.report.source_snapshot.get("source_session_date"),
        "target_session_date": result.report.target_session_date.isoformat(),
        "generated_at": (
            result.report.generated_at.isoformat()
            if result.report.generated_at is not None
            else None
        ),
        "universe_size": result.report.source_snapshot.get("universe_size"),
        "notified_users": notified_users,
    }
    logger.info("Daily top-ten scan result: %s", payload)
    return payload


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(asyncio.run(run_daily_top10_scan()), ensure_ascii=False))


if __name__ == "__main__":
    main()
