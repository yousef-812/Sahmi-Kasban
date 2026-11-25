from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EarningsCalendar, User, WalletAccount
from app.services.earnings import (
    get_earnings_calendar,
    refresh_earnings_calendar,
    upsert_earnings_events,
)
from app.services.stock_analysis import execute_stock_analysis

TICKER = "COMI"


def _event(
    ticker: str = TICKER,
    *,
    days_ahead: int = 5,
    estimate_eps: float | None = 5.35,
    today: date | None = None,
) -> dict:
    base = today if today is not None else datetime.now(UTC).date()
    return {
        "ticker": ticker,
        "event_date": base + timedelta(days=days_ahead),
        "period": None,
        "estimate_eps": estimate_eps,
        "raw": {"earnings_release_next_date": 1_794_398_400},
    }


# ─── upsert / read service ───────────────────────────────────────────────────


def test_upsert_inserts_once_then_updates(db_session: Session) -> None:
    assert upsert_earnings_events(db_session, events=[_event()]) == 1
    assert upsert_earnings_events(db_session, events=[_event(estimate_eps=6.1)]) == 1

    rows = db_session.scalars(select(EarningsCalendar)).all()
    assert len(rows) == 1
    assert rows[0].ticker == TICKER
    assert rows[0].period is None
    assert rows[0].source == "tradingview_scanner"
    assert float(rows[0].estimate_eps) == 6.1
    assert rows[0].raw["earnings_release_next_date"] == 1_794_398_400


def test_read_reports_available_false_when_empty(db_session: Session) -> None:
    payload = get_earnings_calendar(db_session, ticker=TICKER, days=30)

    assert payload["available"] is False
    assert payload["source"] is None
    assert payload["items"] == []
    assert payload["as_of"] is None
    assert payload["ticker"] == TICKER
    assert payload["days"] == 30


def test_read_filters_by_ticker_and_window(db_session: Session) -> None:
    today = date(2026, 10, 14)
    upsert_earnings_events(
        db_session,
        events=[
            _event(TICKER, days_ahead=5, today=today),
            _event("ETEL", days_ahead=5, today=today),
            _event(TICKER, days_ahead=40, today=today),
        ],
    )

    window = get_earnings_calendar(db_session, ticker=TICKER, days=30, today=today)
    assert window["available"] is True
    assert window["source"] == "tradingview_scanner"
    assert [item["ticker"] for item in window["items"]] == [TICKER]

    all_tickers = get_earnings_calendar(db_session, days=30, today=today)
    assert len(all_tickers["items"]) == 2

    short = get_earnings_calendar(db_session, days=3, today=today)
    assert short["items"] == []
    assert short["available"] is False
    assert short["source"] is None


def test_refresh_short_circuits_in_test_environment(db_session: Session) -> None:
    result = asyncio.run(refresh_earnings_calendar(db_session))

    assert result["available"] is False
    assert result["source"] is None
    assert result["refreshed"] == 0
    assert result["reason"] == "test_environment"


# ─── GET /market/earnings-calendar ──────────────────────────────────────────


def test_endpoint_returns_200_empty_with_source_null(client: TestClient) -> None:
    response = client.get("/api/v1/market/earnings-calendar")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert payload["source"] is None
    assert payload["items"] == []
    assert payload["days"] == 30
    assert payload["ticker"] is None
    assert payload["as_of"] is None


def test_endpoint_returns_seeded_events(client: TestClient, db_session: Session) -> None:
    upsert_earnings_events(db_session, events=[_event(days_ahead=2)])

    response = client.get(
        "/api/v1/market/earnings-calendar",
        params={"ticker": TICKER, "days": 30},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["source"] == "tradingview_scanner"
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["ticker"] == TICKER
    assert item["event_date"] == (datetime.now(UTC).date() + timedelta(days=2)).isoformat()
    assert item["estimate_eps"] == 5.35
    assert item["source"] == "tradingview_scanner"


def test_endpoint_rejects_invalid_ticker_and_days(client: TestClient) -> None:
    assert (
        client.get(
            "/api/v1/market/earnings-calendar",
            params={"ticker": "bad!!ticker"},
        ).status_code
        == 404
    )
    assert (
        client.get("/api/v1/market/earnings-calendar", params={"days": 0}).status_code == 422
    )
    assert (
        client.get("/api/v1/market/earnings-calendar", params={"days": 400}).status_code == 422
    )


# ─── stock_analysis wiring ──────────────────────────────────────────────────


class FakeMarketDataProvider:
    name = "fake"

    def __init__(self) -> None:
        self.calls = 0

    async def get_history(self, ticker: str, *, period: str, interval: str):
        from app.market_data.types import CandleSeries

        self.calls += 1
        start = datetime(2025, 9, 1, tzinfo=UTC)
        candles: list[dict[str, object]] = []
        for index in range(220):
            close = 100 + (index * 0.15) + ((index % 7) * 0.05)
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": round(close - 0.3, 6),
                    "high": round(close + 0.8, 6),
                    "low": round(close - 0.9, 6),
                    "close": round(close, 6),
                    "volume": 1_000_000 + (index * 1000),
                }
            )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 25, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="e" * 64,
            candles=tuple(candles),
        )


class FakeStockAIService:
    async def explain_stock_analysis(
        self, *, ticker: str, analysis_payload: dict, language: str = "ar"
    ) -> str:
        return f"AI explanation for {ticker} in {language}"


def _seed_user(db: Session) -> User:
    user = User(
        email="earnings-wiring@example.com",
        password_hash="hashed-password",
        display_name="Earnings User",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
        auth_version=0,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=1000))
    db.commit()
    return user


def _run_analysis(db: Session, monkeypatch, *, enable_fundamentals, metric_factory=None):
    from app.services import stock_analysis as stock_analysis_module

    def _unexpected(db, ticker):
        raise AssertionError("get_stock_investment_metric must not run when the flag is off")

    real_get_settings = stock_analysis_module.get_settings
    monkeypatch.setattr(
        stock_analysis_module,
        "get_settings",
        lambda: real_get_settings().model_copy(
            update={"analysis_enable_fundamentals": enable_fundamentals}
        ),
    )
    monkeypatch.setattr(
        stock_analysis_module,
        "get_stock_investment_metric",
        metric_factory or _unexpected,
    )
    return asyncio.run(
        execute_stock_analysis(
            db,
            user=_seed_user(db),
            ticker=TICKER,
            provider=FakeMarketDataProvider(),
            ai_service=FakeStockAIService(),
        )
    )


def test_wiring_flag_off_never_touches_fundamentals(db_session: Session, monkeypatch) -> None:
    execution = _run_analysis(db_session, monkeypatch, enable_fundamentals=False)

    engines = execution.analysis.payload["analysis"]["engines"]
    assert "investment" not in engines
    assert execution.cached is False


def test_wiring_flag_on_blends_fundamentals_context(db_session: Session, monkeypatch) -> None:
    async def _metric(db, ticker):
        return {
            "pe_ratio": 5.5,
            "pb_ratio": 1.1,
            "dividend_yield_pct": 9.5,
            "roe_pct": 25.0,
            "total_debt": 100_000_000,
            "market_cap": 3_000_000_000,
            "net_income": 1_000_000_000,
            "eps": 4.2,
        }

    execution = _run_analysis(
        db_session,
        monkeypatch,
        enable_fundamentals=True,
        metric_factory=_metric,
    )

    payload = execution.analysis.payload["analysis"]
    engines = payload["engines"]
    assert "investment" in engines
    assert engines["investment"]["status"] == "complete"
    assert engines["investment"]["score"] > 60.0
    assert engines["investment"]["details"]["pe_ratio"] == 5.5
    assert engines["investment"]["details"]["ticker"] == TICKER

    quality = payload["analysis_quality"]
    for bucket in ("bullish_engines", "bearish_engines", "neutral_engines"):
        assert "investment" not in quality[bucket]


def test_wiring_survives_fundamentals_failure(db_session: Session, monkeypatch) -> None:
    def _boom(db, ticker):
        raise RuntimeError("fundamental scanner exploded")

    execution = _run_analysis(
        db_session,
        monkeypatch,
        enable_fundamentals=True,
        metric_factory=_boom,
    )

    engines = execution.analysis.payload["analysis"]["engines"]
    assert execution.cached is False
    assert "investment" in engines
    assert engines["investment"]["status"] == "complete"
    assert engines["news_sentiment"]["score"] == 50.0
