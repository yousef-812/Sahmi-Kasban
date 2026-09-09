from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from app.market_calendar import (
    EGXTradingCalendar,
    NonTradingSessionError,
    ScanNotDueError,
)


def _calendar(*, holidays: frozenset[date] = frozenset()) -> EGXTradingCalendar:
    return EGXTradingCalendar(
        timezone_name="Africa/Cairo",
        holidays=holidays,
        scan_hour=15,
        scan_minute=0,
    )


def test_calendar_skips_friday_saturday_and_configured_holiday() -> None:
    holiday = date(2026, 7, 27)
    calendar = _calendar(holidays=frozenset({holiday}))

    assert calendar.is_trading_session(date(2026, 7, 26)) is True
    assert calendar.is_trading_session(holiday) is False
    assert calendar.is_trading_session(date(2026, 7, 31)) is False
    assert calendar.is_trading_session(date(2026, 8, 1)) is False
    assert calendar.next_trading_session(date(2026, 7, 26)) == date(2026, 7, 28)


def test_scan_requires_three_pm_cairo_on_a_trading_day() -> None:
    calendar = _calendar()
    zone = ZoneInfo("Africa/Cairo")

    with pytest.raises(ScanNotDueError):
        calendar.resolve_scan_session(datetime(2026, 7, 26, 14, 59, tzinfo=zone))

    session = calendar.resolve_scan_session(datetime(2026, 7, 26, 15, 0, tzinfo=zone))
    assert session.source_session_date == date(2026, 7, 26)
    assert session.target_session_date == date(2026, 7, 27)
    assert session.scheduled_for.hour == 15


def test_scan_does_not_run_on_weekend() -> None:
    calendar = _calendar()
    zone = ZoneInfo("Africa/Cairo")

    with pytest.raises(NonTradingSessionError):
        calendar.resolve_scan_session(datetime(2026, 7, 31, 18, 0, tzinfo=zone))


def test_upcoming_sessions_span_only_current_week() -> None:
    calendar = _calendar()
    zone = ZoneInfo("Africa/Cairo")

    # Sunday 6/9 after 10:00 -> Monday 7/9 through Thursday 10/9 (same week only).
    sessions = calendar.get_upcoming_trading_sessions(
        datetime(2026, 9, 6, 12, 0, tzinfo=zone)
    )
    assert [item["date"] for item in sessions] == [
        "2026-09-07",
        "2026-09-08",
        "2026-09-09",
        "2026-09-10",
    ]
    assert sessions[0]["is_next_session"] is True
    assert all(item["is_next_session"] is False for item in sessions[1:])


def test_upcoming_sessions_include_today_before_ten_am() -> None:
    calendar = _calendar()
    zone = ZoneInfo("Africa/Cairo")

    # Tuesday 8/9 before 10:00 -> today's session still available.
    sessions = calendar.get_upcoming_trading_sessions(
        datetime(2026, 9, 8, 9, 0, tzinfo=zone)
    )
    assert [item["date"] for item in sessions] == [
        "2026-09-08",
        "2026-09-09",
        "2026-09-10",
    ]


def test_upcoming_sessions_roll_to_next_week_after_thursday() -> None:
    calendar = _calendar()
    zone = ZoneInfo("Africa/Cairo")

    # Thursday 10/9 after 10:00 -> next trading week starts Sunday 13/9.
    sessions = calendar.get_upcoming_trading_sessions(
        datetime(2026, 9, 10, 12, 0, tzinfo=zone)
    )
    assert [item["date"] for item in sessions] == [
        "2026-09-13",
        "2026-09-14",
        "2026-09-15",
        "2026-09-16",
        "2026-09-17",
    ]
