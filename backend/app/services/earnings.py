from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Environment, get_settings
from app.market_data.fundamental import fetch_egx_earnings_events
from app.models import EarningsCalendar

logger = logging.getLogger(__name__)

EARNINGS_SOURCE = "tradingview_scanner"
_REFRESH_INTERVAL = timedelta(hours=12)
_RETRY_INTERVAL = timedelta(minutes=10)

_last_success_at: datetime | None = None
_last_failure_at: datetime | None = None
_refresh_lock = asyncio.Lock()


def upsert_earnings_events(
    db: Session,
    *,
    events: list[dict[str, Any]],
    source: str = EARNINGS_SOURCE,
) -> int:
    """Insert or update calendar rows keyed on ``(ticker, event_date, period)``.

    A select-then-write keeps the upsert correct on both PostgreSQL and SQLite:
    a NULL ``period`` never matches inside ``ON CONFLICT`` there. Only keys
    present in each event are overwritten so a refresh cannot erase data it
    does not carry.
    """
    written = 0
    for event in events:
        ticker = str(event["ticker"])
        event_date: date = event["event_date"]
        period = event.get("period")
        row = db.scalar(
            select(EarningsCalendar).where(
                EarningsCalendar.ticker == ticker,
                EarningsCalendar.event_date == event_date,
                EarningsCalendar.period == period,
            )
        )
        if row is None:
            row = EarningsCalendar(
                ticker=ticker,
                event_date=event_date,
                period=period,
                source=source,
                raw=dict(event.get("raw") or {}),
            )
            db.add(row)
        else:
            row.source = source
            row.raw = dict(event.get("raw") or {})
        if "estimate_eps" in event:
            row.estimate_eps = event.get("estimate_eps")
        if "actual_eps" in event:
            row.actual_eps = event.get("actual_eps")
        written += 1
    db.commit()
    return written


async def refresh_earnings_calendar(db: Session, *, force: bool = False) -> dict[str, Any]:
    """Pull next-earnings dates from the allowed scanner feed and persist them.

    Degrades to ``available: false``/``source: null`` on any failure — the
    calendar is never populated with guessed dates. Successes are reused for
    12 hours and failures back off for 10 minutes so a failing feed is not
    hammered by the read endpoint; ``force=True`` bypasses both.
    """
    global _last_success_at, _last_failure_at

    if get_settings().app_env is Environment.TEST:
        return {
            "available": False,
            "source": None,
            "refreshed": 0,
            "reason": "test_environment",
        }

    now = datetime.now(UTC)
    if not force:
        if _last_success_at is not None and now - _last_success_at < _REFRESH_INTERVAL:
            return {
                "available": True,
                "source": EARNINGS_SOURCE,
                "refreshed": 0,
                "reason": "cached",
            }
        if _last_failure_at is not None and now - _last_failure_at < _RETRY_INTERVAL:
            return {
                "available": False,
                "source": None,
                "refreshed": 0,
                "reason": "fetch_failed",
            }

    async with _refresh_lock:
        try:
            events = await fetch_egx_earnings_events()
            refreshed = upsert_earnings_events(db, events=events)
        except Exception as exc:
            _last_failure_at = now
            logger.warning("Earnings calendar refresh failed: %s", exc)
            db.rollback()
            return {
                "available": False,
                "source": None,
                "refreshed": 0,
                "reason": "fetch_failed",
            }
        _last_success_at = now
        _last_failure_at = None

    if not events:
        return {
            "available": False,
            "source": None,
            "refreshed": 0,
            "reason": "no_events",
        }
    return {
        "available": True,
        "source": EARNINGS_SOURCE,
        "refreshed": refreshed,
        "reason": None,
    }


def get_earnings_calendar(
    db: Session,
    *,
    ticker: str | None = None,
    days: int = 30,
    today: date | None = None,
) -> dict[str, Any]:
    """Read persisted earnings events in ``[today, today + days]``.

    Read-only: it never fetches or guesses. When nothing real is stored the
    response is ``available: false`` with ``source: null`` and an empty list.
    """
    start = today if today is not None else datetime.now(UTC).date()
    end = start + timedelta(days=max(0, days))
    stmt = (
        select(EarningsCalendar)
        .where(
            EarningsCalendar.event_date >= start,
            EarningsCalendar.event_date <= end,
        )
        .order_by(EarningsCalendar.event_date.asc())
    )
    if ticker:
        stmt = stmt.where(EarningsCalendar.ticker == ticker)
    rows = db.scalars(stmt).all()

    items: list[dict[str, Any]] = [
        {
            "ticker": row.ticker,
            "event_date": row.event_date,
            "period": row.period,
            "estimate_eps": (
                float(row.estimate_eps) if row.estimate_eps is not None else None
            ),
            "actual_eps": float(row.actual_eps) if row.actual_eps is not None else None,
            "source": row.source,
        }
        for row in rows
    ]
    return {
        "ticker": ticker,
        "days": days,
        "available": bool(items),
        "source": items[0]["source"] if items else None,
        "items": items,
        "as_of": max((row.updated_at for row in rows), default=None),
    }
