"""WP-30: volume-profile endpoint computed from cached OHLCV candles."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.market_data.types import MarketDataUnavailableError
from app.models import MarketDataSnapshot
from app.services import volume_profile

TICKER = "COMI"


def _climbing_candles(count: int = 40) -> list[dict[str, object]]:
    candles: list[dict[str, object]] = []
    close = 100.0
    for index in range(count):
        opened = close
        close = opened + 1.0
        candles.append(
            {
                "timestamp": (datetime(2026, 6, 1, tzinfo=UTC) + timedelta(days=index)).isoformat(),
                "open": opened,
                "high": close + 0.5,
                "low": opened - 0.5,
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


def test_volume_profile_bins_sum_to_candle_volume(client: TestClient, db_session: Session) -> None:
    candles = _climbing_candles()
    _seed_candles(db_session, TICKER, candles)

    response = client.get("/api/v1/stocks/COMI/volume-profile")

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["ticker"] == TICKER
    assert len(body["bins"]) >= 2
    total = sum(bin_["volume"] for bin_ in body["bins"])
    assert total == pytest.approx(40 * 1_000.0, rel=1e-3)
    assert body["value_area_low"] <= body["poc"] <= body["value_area_high"]
    assert body["above_value_pct"] + body["below_value_pct"] <= 30.5
    assert body["window_days"] == 40
    assert body["as_of"] is not None
    assert body["reason"] is None


def test_volume_profile_window_follows_days_parameter(client: TestClient, db_session: Session) -> None:
    _seed_candles(db_session, TICKER, _climbing_candles())

    body = client.get("/api/v1/stocks/COMI/volume-profile", params={"days": 10}).json()

    assert body["available"] is True
    assert body["window_days"] == 10


def test_volume_profile_unavailable_when_history_cannot_load(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _boom(*args: object, **kwargs: object):
        raise MarketDataUnavailableError("provider down")

    monkeypatch.setattr(volume_profile, "get_cached_or_fresh_history", _boom)

    body = client.get("/api/v1/stocks/COMI/volume-profile").json()

    assert body["available"] is False
    assert body["bins"] == []
    assert body["poc"] is None
    assert "provider down" in body["reason"]


def test_volume_profile_rejects_invalid_requests(client: TestClient) -> None:
    assert client.get("/api/v1/stocks/bad!!ticker/volume-profile").status_code == 404
    assert client.get("/api/v1/stocks/COMI/volume-profile", params={"days": 4}).status_code == 422
    assert client.get("/api/v1/stocks/COMI/volume-profile", params={"days": 251}).status_code == 422
