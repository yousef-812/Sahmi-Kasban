from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.config import get_settings


class MarketCalendarError(RuntimeError):
    """Base error for market-calendar decisions."""


class ScanNotDueError(MarketCalendarError):
    """Raised when the daily scan is called before its configured time."""


class NonTradingSessionError(MarketCalendarError):
    """Raised when a scan is requested for a weekend or configured holiday."""


@dataclass(frozen=True, slots=True)
class ScanSession:
    source_session_date: date
    target_session_date: date
    scheduled_for: datetime


SESSION_START_TIME = time(hour=10, minute=0)
SESSION_END_TIME = time(hour=14, minute=30)


class EGXTradingCalendar:
    """Deterministic EGX session calendar with configurable holidays."""

    weekend_weekdays = frozenset({4, 5})  # Friday and Saturday.

    def __init__(
        self,
        *,
        timezone_name: str,
        holidays: frozenset[date],
        scan_hour: int,
        scan_minute: int,
    ) -> None:
        self.timezone = ZoneInfo(timezone_name)
        self.holidays = holidays
        self.scan_time = time(hour=scan_hour, minute=scan_minute)

    @classmethod
    def from_settings(cls) -> EGXTradingCalendar:
        settings = get_settings()
        holidays: set[date] = set()
        for raw_value in settings.egx_holidays.split(","):
            value = raw_value.strip()
            if value:
                holidays.add(date.fromisoformat(value))
        return cls(
            timezone_name=settings.market_timezone,
            holidays=frozenset(holidays),
            scan_hour=settings.daily_scan_hour,
            scan_minute=settings.daily_scan_minute,
        )

    def is_trading_session(self, session_date: date) -> bool:
        return session_date.weekday() not in self.weekend_weekdays and session_date not in self.holidays

    def next_trading_session(self, after_date: date) -> date:
        candidate = after_date + timedelta(days=1)
        for _ in range(370):
            if self.is_trading_session(candidate):
                return candidate
            candidate += timedelta(days=1)
        raise MarketCalendarError("Could not resolve the next EGX trading session")

    def resolve_scan_session(self, moment: datetime | None = None) -> ScanSession:
        current = moment or datetime.now(UTC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=UTC)
        local = current.astimezone(self.timezone)
        source_date = local.date()
        if not self.is_trading_session(source_date):
            raise NonTradingSessionError(f"{source_date.isoformat()} is not an EGX trading session")
        if local.timetz().replace(tzinfo=None) < self.scan_time:
            raise ScanNotDueError(
                f"Daily scan is scheduled for {self.scan_time.isoformat(timespec='minutes')} "
                f"in {self.timezone.key}"
            )
        scheduled_for = datetime.combine(
            source_date,
            self.scan_time,
            tzinfo=self.timezone,
        )
        return ScanSession(
            source_session_date=source_date,
            target_session_date=self.next_trading_session(source_date),
            scheduled_for=scheduled_for,
        )

    def resolve_prediction_target_session(self, moment: datetime | None = None) -> date:
        current = moment or datetime.now(UTC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=UTC)
        local = current.astimezone(self.timezone)
        today = local.date()

        if self.is_trading_session(today):
            if local.time() < SESSION_START_TIME:
                return today
            return self.next_trading_session(today)
        return self.next_trading_session(today)

    def _week_thursday(self, session_date: date) -> date:
        # EGX trading week is Sunday-Thursday; find the Thursday closing this week.
        days_until_thursday = (3 - session_date.weekday()) % 7
        return session_date + timedelta(days=days_until_thursday)

    def get_upcoming_trading_sessions(
        self,
        moment: datetime | None = None,
        count: int = 5,
    ) -> list[dict[str, object]]:
        first_target = self.resolve_prediction_target_session(moment)
        week_end = self._week_thursday(first_target)
        sessions: list[dict[str, object]] = []

        curr = first_target
        while curr <= week_end and len(sessions) < count:
            sessions.append({
                "date": curr.isoformat(),
                "display_name": format_arabic_date(curr),
                "is_next_session": len(sessions) == 0,
            })
            curr = self.next_trading_session(curr)

        return sessions


ARABIC_DAY_NAMES: dict[int, str] = {
    0: "الاثنين",
    1: "الثلاثاء",
    2: "الأربعاء",
    3: "الخميس",
    4: "الجمعة",
    5: "السبت",
    6: "الأحد",
}

ARABIC_MONTH_NAMES: dict[int, str] = {
    1: "يناير",
    2: "فبراير",
    3: "مارس",
    4: "أبريل",
    5: "مايو",
    6: "يونيو",
    7: "يوليو",
    8: "أغسطس",
    9: "سبتمبر",
    10: "أكتوبر",
    11: "نوفمبر",
    12: "ديسمبر",
}


def format_arabic_date(d: date) -> str:
    day_name = ARABIC_DAY_NAMES[d.weekday()]
    month_name = ARABIC_MONTH_NAMES[d.month]
    return f"{day_name} {d.day} {month_name} {d.year}"

