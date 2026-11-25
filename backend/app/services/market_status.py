from __future__ import annotations

from datetime import UTC, datetime

from app.market_calendar import (
    SESSION_END_TIME,
    SESSION_START_TIME,
    EGXTradingCalendar,
)

DAY_NAMES: tuple[str, ...] = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


def market_status(now: datetime | None = None) -> dict:
    """Authoritative EGX open/closed state for ``now`` (single source of truth).

    Session window is ``SESSION_START_TIME``..``SESSION_END_TIME`` (10:00-14:30)
    in the configured market timezone (Africa/Cairo), Sunday through Thursday,
    skipping the configured ``EGX_HOLIDAYS``.
    """
    calendar = EGXTradingCalendar.from_settings()
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    local = current.astimezone(calendar.timezone)
    local_time = local.timetz().replace(tzinfo=None)
    session_date = local.date()

    is_trading_day = calendar.is_trading_session(session_date)
    is_open = is_trading_day and SESSION_START_TIME <= local_time < SESSION_END_TIME

    if is_trading_day and local_time < SESSION_START_TIME:
        next_open_date = session_date
    else:
        next_open_date = calendar.next_trading_session(session_date)

    if is_trading_day and local_time < SESSION_END_TIME:
        next_close_date = session_date
    else:
        next_close_date = calendar.next_trading_session(session_date)

    next_open = datetime.combine(next_open_date, SESSION_START_TIME, tzinfo=calendar.timezone)
    next_close = datetime.combine(next_close_date, SESSION_END_TIME, tzinfo=calendar.timezone)

    return {
        "is_open": is_open,
        "session": {
            "opens_at": SESSION_START_TIME.isoformat(timespec="minutes"),
            "closes_at": SESSION_END_TIME.isoformat(timespec="minutes"),
        },
        "timezone": calendar.timezone.key,
        "date": session_date.isoformat(),
        "next_open": next_open.isoformat(),
        "next_close": next_close.isoformat(),
        "day": DAY_NAMES[local.weekday()],
        "is_trading_day": is_trading_day,
    }
