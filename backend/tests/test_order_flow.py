from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.market_data import order_flow, top_of_book
from app.market_data.quotes import MarketQuote
from app.models import MarketDataSnapshot

PASSWORD = "StrongPass123"

BASE_SESSION = datetime(2026, 9, 27, tzinfo=UTC)

NO_DEPTH_REASON = "No depth-capable market-data provider is configured"


def _register_and_login(client: TestClient, fake_email_service, *, email: str) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "display_name": "Order Flow Tester"},
    )
    assert registered.status_code == 201
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verified.status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _steady_sessions_with_spike(*, spike_volume: float = 50_000_000.0) -> list[dict[str, object]]:
    sessions: list[dict[str, object]] = []
    for index in range(12):
        volume = spike_volume if index == 11 else 1_000_000.0
        day = (BASE_SESSION + timedelta(days=index)).date().isoformat()
        sessions.append({"day": day, "price": 100.0, "volume": volume})
    return sessions


def _add_daily_snapshot(db: Session, ticker: str, sessions: list[dict[str, object]]) -> None:
    candles = [
        {
            "timestamp": f"{session['day']}T10:00:00+00:00",
            "open": session["price"],
            "high": session["price"],
            "low": session["price"],
            "close": session["price"],
            "volume": session["volume"],
        }
        for session in sessions
    ]
    now = datetime.now(UTC)
    db.add(
        MarketDataSnapshot(
            ticker=ticker,
            provider="stub",
            interval="1d",
            period="1y",
            data_as_of=now,
            fetched_at=now,
            expires_at=now + timedelta(hours=1),
            fingerprint="b" * 64,
            candle_count=len(candles),
            payload={"candles": candles},
        )
    )
    db.commit()


def _make_quote(
    ticker: str,
    *,
    volume: float,
    price: float,
    session_date: str,
) -> MarketQuote:
    return MarketQuote(
        ticker=ticker,
        description="",
        exchange="EGX",
        sector=None,
        current_price=price,
        open_price=None,
        previous_close=None,
        session_high=None,
        session_low=None,
        change=None,
        change_percent=None,
        volume=volume,
        week52_high=None,
        week52_low=None,
        market_open=True,
        session_change_percent=None,
        session_date=session_date,
        next_session_open=None,
    )


@pytest.fixture(autouse=True)
def stub_live_quote(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_quote(db: Session, ticker: str, *, force_refresh: bool = False) -> None:
        return None

    monkeypatch.setattr(order_flow, "fetch_single_quote", _no_quote)


def test_order_flow_endpoints_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/market/orderbook/COMI").status_code == 401
    assert client.get("/api/v1/market/trades/COMI").status_code == 401
    assert client.get("/api/v1/market/bulk-trades", params={"ticker": "COMI"}).status_code == 401
    assert client.get("/api/v1/market/depth/COMI").status_code == 401


def test_order_book_reports_unavailable(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-book@example.com")

    response = client.get("/api/v1/market/orderbook/COMI", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "available": False,
        "ticker": "COMI",
        "as_of": None,
        "bids": [],
        "asks": [],
        "provider": None,
        "reason": NO_DEPTH_REASON,
    }


def test_recent_trades_reports_unavailable(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-trades@example.com")

    response = client.get("/api/v1/market/trades/COMI", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "available": False,
        "ticker": "COMI",
        "items": [],
        "provider": None,
        "reason": NO_DEPTH_REASON,
    }


def test_depth_reports_unavailable_with_zeroed_aggregates(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-depth@example.com")

    response = client.get("/api/v1/market/depth/COMI", params={"levels": 5}, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "available": False,
        "ticker": "COMI",
        "as_of": None,
        "levels": 5,
        "bid_levels": [],
        "ask_levels": [],
        "total_bid_volume": 0.0,
        "total_ask_volume": 0.0,
        "spread": None,
        "mid_price": None,
        "provider": None,
        "reason": NO_DEPTH_REASON,
    }


def test_invalid_limit_levels_and_threshold_are_rejected(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-422@example.com")

    assert client.get("/api/v1/market/trades/COMI", params={"limit": 0}, headers=headers).status_code == 422
    assert (
        client.get("/api/v1/market/trades/COMI", params={"limit": 1001}, headers=headers).status_code == 422
    )
    assert client.get("/api/v1/market/depth/COMI", params={"levels": 0}, headers=headers).status_code == 422
    assert client.get("/api/v1/market/depth/COMI", params={"levels": 51}, headers=headers).status_code == 422
    assert (
        client.get(
            "/api/v1/market/bulk-trades",
            params={"ticker": "COMI", "value_threshold": 0},
            headers=headers,
        ).status_code
        == 422
    )
    assert client.get("/api/v1/market/bulk-trades", headers=headers).status_code == 422


def test_unknown_ticker_returns_404(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-404@example.com")

    assert client.get("/api/v1/market/orderbook/ZZZZ", headers=headers).status_code == 404
    assert client.get("/api/v1/market/trades/ZZZZ", headers=headers).status_code == 404
    assert client.get("/api/v1/market/depth/ZZZZ", headers=headers).status_code == 404
    assert (
        client.get("/api/v1/market/bulk-trades", params={"ticker": "ZZZZ"}, headers=headers).status_code
        == 404
    )
    assert client.get("/api/v1/market/orderbook/BAD!", headers=headers).status_code == 404


def test_bulk_trades_unavailable_without_daily_history(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-whales-none@example.com")

    response = client.get("/api/v1/market/bulk-trades", params={"ticker": "COMI"}, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"available": False, "ticker": "COMI", "threshold": None, "items": []}


def test_bulk_trades_flags_high_turnover_sessions(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-whales@example.com")
    _add_daily_snapshot(db_session, "COMI", _steady_sessions_with_spike())

    response = client.get("/api/v1/market/bulk-trades", params={"ticker": "COMI"}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["ticker"] == "COMI"
    assert body["threshold"] == pytest.approx(300_000_000.0)
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["session_date"] == "2026-10-08"
    assert item["close"] == pytest.approx(100.0)
    assert item["volume"] == pytest.approx(50_000_000.0)
    assert item["turnover_egp"] == pytest.approx(5_000_000_000.0)
    assert item["turnover_ratio"] == pytest.approx(50.0)


def test_bulk_trades_honors_user_value_threshold(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-threshold@example.com")
    _add_daily_snapshot(db_session, "COMI", _steady_sessions_with_spike())

    response = client.get(
        "/api/v1/market/bulk-trades",
        params={"ticker": "COMI", "value_threshold": 6_000_000_000},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["threshold"] == pytest.approx(6_000_000_000.0)
    assert body["items"] == []

    lowered = client.get(
        "/api/v1/market/bulk-trades",
        params={"ticker": "COMI", "value_threshold": 500_000_000},
        headers=headers,
    ).json()
    assert [item["session_date"] for item in lowered["items"]] == ["2026-10-08"]


def test_bulk_trades_includes_live_session_turnover(
    client: TestClient, fake_email_service, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-live@example.com")
    _add_daily_snapshot(db_session, "COMI", _steady_sessions_with_spike(spike_volume=1_000_000.0))

    async def _live_quote(db: Session, ticker: str, *, force_refresh: bool = False) -> MarketQuote:
        return _make_quote(ticker, volume=40_000_000.0, price=100.0, session_date="2026-10-09")

    monkeypatch.setattr(order_flow, "fetch_single_quote", _live_quote)

    response = client.get("/api/v1/market/bulk-trades", params={"ticker": "COMI"}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert [item["session_date"] for item in body["items"]] == ["2026-10-09"]
    assert body["items"][0]["turnover_egp"] == pytest.approx(4_000_000_000.0)
    assert body["items"][0]["turnover_ratio"] == pytest.approx(40.0)


def test_bulk_trades_auto_threshold_needs_minimum_history(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="orderflow-short@example.com")
    _add_daily_snapshot(db_session, "COMI", _steady_sessions_with_spike()[:5])

    auto = client.get("/api/v1/market/bulk-trades", params={"ticker": "COMI"}, headers=headers).json()
    assert auto == {"available": False, "ticker": "COMI", "threshold": None, "items": []}

    explicit = client.get(
        "/api/v1/market/bulk-trades",
        params={"ticker": "COMI", "value_threshold": 50_000_000},
        headers=headers,
    ).json()
    assert explicit["available"] is True
    assert explicit["threshold"] == pytest.approx(50_000_000.0)
    assert [item["session_date"] for item in explicit["items"]] == [
        "2026-10-01",
        "2026-09-30",
        "2026-09-29",
        "2026-09-28",
        "2026-09-27",
    ]


def test_service_functions_return_documented_shapes(db_session: Session) -> None:
    order_book = asyncio.run(order_flow.get_order_book(db_session, "comi"))
    assert order_book == {
        "available": False,
        "ticker": "COMI",
        "as_of": None,
        "bids": [],
        "asks": [],
        "provider": None,
        "reason": NO_DEPTH_REASON,
    }

    trades = asyncio.run(order_flow.get_recent_trades(db_session, "comi", limit=50))
    assert trades == {
        "available": False,
        "ticker": "COMI",
        "items": [],
        "provider": None,
        "reason": NO_DEPTH_REASON,
    }

    depth = asyncio.run(order_flow.get_market_depth(db_session, "comi", levels=7))
    assert depth["available"] is False
    assert depth["levels"] == 7
    assert depth["bid_levels"] == [] and depth["ask_levels"] == []
    assert depth["reason"] == NO_DEPTH_REASON

    whales = asyncio.run(order_flow.detect_whales(db_session, "comi"))
    assert whales == {"available": False, "ticker": "COMI", "threshold": None, "items": []}


class _FakeTopOfBookFetcher:
    def __init__(self, quote: dict[str, object]) -> None:
        self.quote = quote
        self.calls = 0

    async def get_realtime_price(self, symbol: str, market: str = "EGX") -> dict[str, object]:
        self.calls += 1
        return self.quote


def _reset_top_of_book_cache() -> None:
    top_of_book._CACHE.clear()


def test_top_of_book_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/market/top-of-book/COMI").status_code == 401


def test_top_of_book_returns_computed_spread(
    client: TestClient, fake_email_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reset_top_of_book_cache()
    fetcher = _FakeTopOfBookFetcher(
        {
            "symbol": "COMI",
            "bid": 99.0,
            "ask": 100.0,
            "price": 99.5,
            "source": "tradingview_realtime",
        }
    )
    monkeypatch.setattr(top_of_book, "_get_fetcher", lambda: fetcher)
    headers = _register_and_login(client, fake_email_service, email="topofbook-ok@example.com")

    response = client.get("/api/v1/market/top-of-book/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["ticker"] == "COMI"
    assert body["bid"] == pytest.approx(99.0)
    assert body["ask"] == pytest.approx(100.0)
    assert body["mid_price"] == pytest.approx(99.5)
    assert body["spread"] == pytest.approx(1.0)
    assert body["spread_bp"] == pytest.approx(100.5051, rel=1e-3)
    assert body["source"] == "tradingview_realtime"
    assert body["reason"] is None
    assert body["as_of"] is not None


def test_top_of_book_caches_successful_payload(
    client: TestClient, fake_email_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reset_top_of_book_cache()
    fetcher = _FakeTopOfBookFetcher({"bid": 50.0, "ask": 51.0, "source": "tradingview_realtime"})
    monkeypatch.setattr(top_of_book, "_get_fetcher", lambda: fetcher)
    headers = _register_and_login(client, fake_email_service, email="topofbook-cache@example.com")

    first = client.get("/api/v1/market/top-of-book/COMI", headers=headers)
    second = client.get("/api/v1/market/top-of-book/COMI", headers=headers)

    assert first.status_code == 200 and second.status_code == 200
    assert fetcher.calls == 1


def test_top_of_book_unavailable_when_bid_or_ask_missing(
    client: TestClient, fake_email_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reset_top_of_book_cache()
    fetcher = _FakeTopOfBookFetcher({"bid": None, "ask": None, "source": "tradingview_realtime"})
    monkeypatch.setattr(top_of_book, "_get_fetcher", lambda: fetcher)
    headers = _register_and_login(client, fake_email_service, email="topofbook-none@example.com")

    response = client.get("/api/v1/market/top-of-book/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is False
    assert body["bid"] is None and body["ask"] is None
    assert body["reason"] == top_of_book._UNAVAILABLE_REASON


def test_top_of_book_unavailable_when_feed_source_is_down(
    client: TestClient, fake_email_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reset_top_of_book_cache()
    fetcher = _FakeTopOfBookFetcher({"source": "unavailable"})
    monkeypatch.setattr(top_of_book, "_get_fetcher", lambda: fetcher)
    headers = _register_and_login(client, fake_email_service, email="topofbook-down@example.com")

    response = client.get("/api/v1/market/top-of-book/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is False
    assert body["source"] == "unavailable"
    assert body["reason"] == top_of_book._UNAVAILABLE_REASON


def test_top_of_book_unknown_ticker_returns_404(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="topofbook-404@example.com")
    assert client.get("/api/v1/market/top-of-book/ZZZZ", headers=headers).status_code == 404


def test_top_of_book_normalizes_ticker_case(
    client: TestClient, fake_email_service, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reset_top_of_book_cache()
    fetcher = _FakeTopOfBookFetcher({"bid": 10.0, "ask": 11.0, "source": "tradingview_realtime"})
    monkeypatch.setattr(top_of_book, "_get_fetcher", lambda: fetcher)
    headers = _register_and_login(client, fake_email_service, email="topofbook-case@example.com")

    response = client.get("/api/v1/market/top-of-book/comi", headers=headers)

    assert response.status_code == 200
    assert response.json()["ticker"] == "COMI"
