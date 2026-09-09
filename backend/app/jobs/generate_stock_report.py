from __future__ import annotations

import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import desc, select

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.market_calendar import EGXTradingCalendar
from app.market_data.provider import get_market_data_provider
from app.models import MarketDataSnapshot
from app.services.stock_report import (
    generate_stock_report,
    persist_stock_report_snapshot,
)

logger = logging.getLogger(__name__)


async def run_stock_report_scan(moment: datetime | None = None) -> dict[str, object]:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    current = moment or datetime.now(UTC)
    local = current.astimezone(tz)
    calendar = EGXTradingCalendar.from_settings()

    source_date = local.date()
    if not calendar.is_trading_session(source_date):
        return {
            "status": "skipped",
            "reason": "non_trading_session",
            "detail": f"{source_date.isoformat()} is not an EGX trading session",
        }

    target_hour = settings.investment_scan_hour
    target_minute = settings.investment_scan_minute
    if (local.hour, local.minute) < (target_hour, target_minute):
        return {
            "status": "skipped",
            "reason": "before_scan_time",
            "detail": f"Stock report scheduled for {target_hour:02d}:{target_minute:02d} Cairo time",
        }

    with SessionLocal() as db:
        snapshot = db.scalar(
            select(MarketDataSnapshot)
            .where(MarketDataSnapshot.ticker == "__STOCK_REPORT__")
            .order_by(desc(MarketDataSnapshot.fetched_at))
        )
        if snapshot is not None and snapshot.fetched_at is not None:
            snap_local_date = snapshot.fetched_at.astimezone(tz).date()
            if snap_local_date == source_date:
                return {
                    "status": "already_exists",
                    "reason": "today_report_present",
                    "fetched_at": snapshot.fetched_at.isoformat(),
                }

        try:
            provider = get_market_data_provider()
            result = await generate_stock_report(db, provider=provider)
            persist_stock_report_snapshot(db, result)

            return {
                "status": "created",
                "undervalued_count": len(result.undervalued),
                "dropped_count": len(result.dropped),
                "bounce_count": len(result.bounce_candidates),
            }
        except Exception as exc:
            db.rollback()
            logger.exception("Scheduled stock report scan failed")
            return {
                "status": "failed",
                "error": str(exc),
            }
