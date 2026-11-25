from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.market_data.quotes import _session_state
from app.services.market_status import market_status

CAIRO = ZoneInfo("Africa/Cairo")

DOCUMENTED_KEYS = {
    "is_open",
    "session",
    "timezone",
    "date",
    "next_open",
    "next_close",
    "day",
    "is_trading_day",
}


def test_mid_session_thursday_is_open() -> None:
    status = market_status(datetime(2026, 9, 10, 11, 0, tzinfo=CAIRO))

    assert status["is_open"] is True
    assert status["is_trading_day"] is True
    assert status["session"] == {"opens_at": "10:00", "closes_at": "14:30"}
    assert status["timezone"] == "Africa/Cairo"
    assert status["date"] == "2026-09-10"
    assert status["day"] == "thursday"
    # Mid-session: the next open is Sunday, the current session still closes today.
    assert status["next_open"].startswith("2026-09-13T10:00")
    assert status["next_close"].startswith("2026-09-10T14:30")


def test_thursday_after_close_is_closed_with_sunday_next_open() -> None:
    status = market_status(datetime(2026, 9, 10, 15, 0, tzinfo=CAIRO))

    assert status["is_open"] is False
    assert status["is_trading_day"] is True
    assert status["date"] == "2026-09-10"
    assert status["next_open"].startswith("2026-09-13T10:00")
    assert status["next_close"].startswith("2026-09-13T14:30")


def test_thursday_before_open_is_closed_and_opens_today() -> None:
    status = market_status(datetime(2026, 9, 10, 9, 0, tzinfo=CAIRO))

    assert status["is_open"] is False
    assert status["is_trading_day"] is True
    assert status["next_open"].startswith("2026-09-10T10:00")
    assert status["next_close"].startswith("2026-09-10T14:30")


@pytest.mark.parametrize(
    ("moment", "day_name", "iso_date"),
    [
        (datetime(2026, 9, 11, 11, 0, tzinfo=CAIRO), "friday", "2026-09-11"),
        (datetime(2026, 9, 12, 11, 0, tzinfo=CAIRO), "saturday", "2026-09-12"),
    ],
)
def test_weekend_is_not_a_trading_day(moment: datetime, day_name: str, iso_date: str) -> None:
    status = market_status(moment)

    assert status["is_trading_day"] is False
    assert status["is_open"] is False
    assert status["day"] == day_name
    assert status["date"] == iso_date
    assert status["next_open"].startswith("2026-09-13T10:00")
    assert status["next_close"].startswith("2026-09-13T14:30")


@pytest.mark.parametrize(
    ("moment", "is_open"),
    [
        (datetime(2026, 9, 10, 9, 59, tzinfo=CAIRO), False),
        (datetime(2026, 9, 10, 10, 0, tzinfo=CAIRO), True),
        (datetime(2026, 9, 10, 14, 29, tzinfo=CAIRO), True),
        (datetime(2026, 9, 10, 14, 30, tzinfo=CAIRO), False),
    ],
)
def test_session_boundaries(moment: datetime, is_open: bool) -> None:
    assert market_status(moment)["is_open"] is is_open


def test_utc_and_naive_moments_are_normalized() -> None:
    utc_moment = market_status(datetime(2026, 9, 10, 8, 0, tzinfo=UTC))
    naive_moment = market_status(datetime(2026, 9, 10, 8, 0))

    assert utc_moment["is_open"] is True
    assert naive_moment["is_open"] is True
    assert naive_moment["date"] == "2026-09-10"


def test_default_now_returns_documented_shape() -> None:
    status = market_status()

    assert set(status) == DOCUMENTED_KEYS
    assert isinstance(status["is_open"], bool)
    assert isinstance(status["is_trading_day"], bool)
    assert status["session"] == {"opens_at": "10:00", "closes_at": "14:30"}
    assert status["timezone"] == "Africa/Cairo"
    assert status["day"] in {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }
    assert len(status["date"]) == 10
    assert datetime.fromisoformat(status["next_open"]) is not None
    assert datetime.fromisoformat(status["next_close"]) is not None


def test_market_status_endpoint_returns_documented_shape(client: TestClient) -> None:
    response = client.get("/api/v1/market/status")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == DOCUMENTED_KEYS
    assert isinstance(payload["is_open"], bool)
    assert isinstance(payload["is_trading_day"], bool)
    assert payload["session"] == {"opens_at": "10:00", "closes_at": "14:30"}
    assert payload["timezone"] == "Africa/Cairo"
    assert datetime.fromisoformat(payload["next_open"]) is not None
    assert datetime.fromisoformat(payload["next_close"]) is not None


def test_quotes_session_state_delegates_to_market_status() -> None:
    moment = datetime(2026, 9, 10, 8, 0, tzinfo=UTC)

    state = _session_state(moment)
    status = market_status(moment)

    assert state.market_open == status["is_open"] is True
    assert state.session_date == date.fromisoformat(status["date"])
    assert state.next_session_open.isoformat() == status["next_open"]
    assert state.reset_change_percent is False


def test_quotes_session_state_on_weekend_is_closed() -> None:
    state = _session_state(datetime(2026, 9, 12, 8, 0, tzinfo=UTC))

    assert state.market_open is False
    assert state.session_date is None
    assert state.next_session_open.isoformat().startswith("2026-09-13T10:00")
