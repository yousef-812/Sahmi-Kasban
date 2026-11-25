"""WP-29: buy/sell pressure endpoint computed from cached OHLCV candles."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.market_data.types import MarketDataUnavailableError
from app.models import MarketDataSnapshot
from app.services import stock_flow

TICKER = "COMI"


def _bullish_candles(count: int = 40) -> list[dict[str, object]]:
    candles: list[dict[str, object]] = []
    close = 100.0
    for index in range(count):
        opened = close
        close = opened + 1.0
        candles.append(
            {
                "timestamp": (datetime(2026, 6, 1, tzinfo=UTC) + timedelta(days=index)).isoformat(),
                "open": opened,
                "high": close,  # H=C وL=O → CLV=+1
                "low": opened,
                "close": close,
                "volume": 1_000.0,
            }
        )
    return candles


def _bearish_candles(count: int = 40) -> list[dict[str, object]]:
    candles: list[dict[str, object]] = []
    close = 100.0
    for index in range(count):
        opened = close
        close = opened - 1.0
        candles.append(
            {
                "timestamp": (datetime(2026, 6, 1, tzinfo=UTC) + timedelta(days=index)).isoformat(),
                "open": opened,
                "high": opened,  # H=O وL=C → CLV=-1
                "low": close,
                "close": close,
                "volume": 1_000.0,
            }
        )
    return candles


def _seed_candles(db: Session, ticker: str, candles: list[dict[str, object]]) -> None:
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
            fingerprint="f" * 64,
            candle_count=len(candles),
            payload={"candles": candles},
        )
    )
    db.commit()


def test_flow_reports_accumulate_for_bullish_candles(client: TestClient, db_session: Session) -> None:
    _seed_candles(db_session, TICKER, _bullish_candles())

    response = client.get("/api/v1/stocks/COMI/flow")

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["ticker"] == TICKER
    assert body["verdict"] == "accumulate"
    assert body["buy_share_pct"] == pytest.approx(100.0)
    assert body["sell_share_pct"] == pytest.approx(0.0)
    assert body["net_volume"] > 0
    assert body["ad_trend"] == 1
    assert body["obv_trend"] == 1
    assert body["mfi14"] is not None and body["mfi14"] > 50.0
    assert body["window_days"] == 40
    assert body["as_of"] is not None
    assert body["reason"] is None


def test_flow_reports_distribute_for_bearish_candles(client: TestClient, db_session: Session) -> None:
    _seed_candles(db_session, TICKER, _bearish_candles())

    body = client.get("/api/v1/stocks/COMI/flow").json()

    assert body["available"] is True
    assert body["verdict"] == "distribute"
    assert body["buy_share_pct"] == pytest.approx(0.0)
    assert body["net_volume"] < 0
    assert body["ad_trend"] == -1


def test_flow_window_follows_days_parameter(client: TestClient, db_session: Session) -> None:
    _seed_candles(db_session, TICKER, _bullish_candles())

    body = client.get("/api/v1/stocks/COMI/flow", params={"days": 10}).json()

    assert body["available"] is True
    assert body["window_days"] == 10


def test_flow_unavailable_when_history_cannot_load(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _boom(*args: object, **kwargs: object):
        raise MarketDataUnavailableError("provider down")

    monkeypatch.setattr(stock_flow, "get_cached_or_fresh_history", _boom)

    body = client.get("/api/v1/stocks/COMI/flow").json()

    assert body["available"] is False
    assert body["verdict"] == "neutral"
    assert body["buy_share_pct"] is None
    assert "provider down" in body["reason"]


def test_flow_unknown_and_invalid_tickers_are_rejected(client: TestClient) -> None:
    assert client.get("/api/v1/stocks/bad!!ticker/flow").status_code == 404
    assert client.get("/api/v1/stocks/COMI/flow", params={"days": 0}).status_code == 422
    assert client.get("/api/v1/stocks/COMI/flow", params={"days": 251}).status_code == 422
