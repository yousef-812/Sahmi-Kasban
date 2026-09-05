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
from app.market_data.universe import apply_market_health_quarantine
from app.models import User
from app.services.daily_reports import (
    DailyReportGenerationError,
    DailyScanAlreadyRunningError,
    generate_daily_top10_report,
)
from app.services.notifications import create_notification
from app.services.operations_settings import get_bool_setting
from app.services.report_performance import evaluate_due_market_reports
from app.services.report_selection import enrich_daily_report_selection
from app.services.stock_analysis import get_stock_ai_service

logger = logging.getLogger(__name__)


async def _scan_universe(db) -> tuple[str, ...]:
    await ensure_market_instrument_catalog(db)
    universe = apply_market_health_quarantine(db)
    logger.info(
        "Daily universe health active=%s tradable=%s incompatible=%s quarantined=%s",
        universe.active_catalog_count,
        len(universe.tickers),
        universe.incompatible_symbol_count,
        universe.replay_failure_quarantine_count,
    )
    return universe.tickers or EGX_SEED_SYMBOLS


def _notify_report_ready(db, *, report_id: str, target_session_date: str) -> int:
    if not get_bool_setting(db, "notifications_enabled"):
        return 0
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
            title="تقرير أفضل الفرص اليومية جاهز",
            body=("تم ترتيب أفضل 10 فرص مع تمييز النخبوية المتوازنة والهجومية والشراء المشروط والمخاطر."),
            category="market_report",
            data={
                "report_id": report_id,
                "target_session_date": target_session_date,
                "route": f"/reports/{report_id}",
            },
        )
    db.commit()
    return len(user_ids)


async def run_daily_top10_scan(moment: datetime | None = None) -> dict[str, object]:
    calendar = EGXTradingCalendar.from_settings()
    try:
        session = calendar.resolve_scan_session(moment)
    except ScanNotDueError as exc:
        return {
            "status": "skipped",
            "reason": "before_scan_time",
            "detail": str(exc),
        }
    except NonTradingSessionError as exc:
        return {
            "status": "skipped",
            "reason": "non_trading_session",
            "detail": str(exc),
        }

    with SessionLocal() as db:
        try:
            await evaluate_due_market_reports(
                db,
                provider=get_market_data_provider(),
                moment=moment or datetime.now(UTC),
            )
        except Exception:
            logger.exception("Failed to evaluate due market reports during daily scan")

        try:
            tickers = await _scan_universe(db)
            result = await generate_daily_top10_report(
                db,
                provider=get_market_data_provider(),
                ai_service=get_stock_ai_service(),
                moment=moment or datetime.now(UTC),
                tickers=tickers,
            )
            enriched = enrich_daily_report_selection(db, report_id=result.report.id)
            notification_count = 0
            if result.created:
                notification_count = _notify_report_ready(
                    db,
                    report_id=str(result.report.id),
                    target_session_date=result.report.target_session_date.isoformat(),
                )
        except ScanNotDueError as exc:
            db.rollback()
            return {
                "status": "skipped",
                "reason": "before_scan_time",
                "detail": str(exc),
            }
        except NonTradingSessionError as exc:
            db.rollback()
            return {
                "status": "skipped",
                "reason": "non_trading_session",
                "detail": str(exc),
            }
        except DailyScanAlreadyRunningError as exc:
            db.rollback()
            return {
                "status": "skipped",
                "reason": "already_running",
                "detail": str(exc),
            }
        except DailyReportGenerationError:
            db.rollback()
            logger.exception("Daily top-ten report generation failed")
            raise

    payload = {
        "status": "created" if result.created else "already_exists",
        "report_id": str(result.report.id),
        "scan_run_id": str(result.scan_run.id),
        "source_session_date": result.report.source_snapshot.get("source_session_date"),
        "target_session_date": result.report.target_session_date.isoformat(),
        "generated_at": (
            result.report.generated_at.isoformat() if result.report.generated_at is not None else None
        ),
        "universe_size": len(tickers),
        "notifications_created": notification_count,
        "selection_model": enriched.market_summary.get(
            "selection_model",
            "cross-sectional-top10-v2.3-regime-two-profile",
        ),
        "selection_regime": enriched.market_summary.get("selection_regime"),
    }
    logger.info("Daily top-ten scan result: %s", payload)
    return payload


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(asyncio.run(run_daily_top10_scan()), ensure_ascii=False))


if __name__ == "__main__":
    main()
