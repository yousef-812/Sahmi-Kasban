"""WP-33: market breadth endpoint computed from quotes snapshot."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.market_data.quotes import MarketQuote
from app.market_data.types import MarketDataUnavailableError
from app.services import market_breadth


def _mock_quotes(advancers: int = 40, decliners: int = 20, unchanged: int = 5) -> list[MarketQuote]:
    quotes: list[MarketQuote] = []
    sectors = ["البنوك", "الاتصالات", "الغذاء", "الصناعة"]
    total = advancers + decliners + unchanged
    for i in range(total):
        sector = sectors[i % len(sectors)]
        if i < advancers:
            pct = 1.5
        elif i < advancers + decliners:
            pct = -2.0
        else:
            pct = 0.0
        quote = MarketQuote(
            ticker=f"TICK{i}",
            description=f"Company {i}",
            exchange="EGX",
            sector=sector,
            current_price=100.0 + pct,
            open_price=100.0,
            previous_close=100.0,
            session_high=102.0,
            session_low=98.0,
            change=1.0 if pct > 0 else (-2.0 if pct < 0 else 0.0),
            change_percent=pct,
            volume=1_000_000.0,
            week52_high=120.0,
            week52_low=80.0,
            market_open=True,
            session_change_percent=pct,
            session_date="2026-10-15",
            next_session_open=datetime(2026, 10, 16, 9, 30, tzinfo=UTC),
        )
        quotes.append(quote)
    return quotes


class MockSnapshot:
    def __init__(self, quotes: list[MarketQuote]) -> None:
        self.items = tuple(quotes)
        self.generated_at = datetime(2026, 10, 15, 15, 30, tzinfo=UTC)
        self.market_open = True
        self.next_session_open = datetime(2026, 10, 16, 9, 30, tzinfo=UTC)
        self.source = "tradingview"


def test_breadth_counts_and_ratio(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    quotes = _mock_quotes(advancers=50, decliners=25, unchanged=10)
    snap = MockSnapshot(quotes)

    async def _mock_fetch(db: Session):
        return snap

    monkeypatch.setattr(market_breadth, "fetch_market_quotes", _mock_fetch)

    response = client.get("/api/v1/market/breadth")
    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["advancers"] == 50
    assert body["decliners"] == 25
    assert body["unchanged"] == 10
    assert body["total"] == 85
    assert body["advance_decline_ratio"] == pytest.approx(2.0)
    assert len(body["sector_performance"]) >= 1
    assert body["as_of"] in {"2026-10-15T15:30:00Z", "2026-10-15T15:30:00+00:00"}
    assert body["reason"] is None


def test_breadth_all_decliners_gives_infinite_ratio_handled(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    quotes = _mock_quotes(advancers=0, decliners=30, unchanged=5)
    snap = MockSnapshot(quotes)

    async def _mock_fetch(db: Session):
        return snap

    monkeypatch.setattr(market_breadth, "fetch_market_quotes", _mock_fetch)

    body = client.get("/api/v1/market/breadth").json()
    assert body["available"] is True
    assert body["advancers"] == 0
    assert body["advance_decline_ratio"] == 0.0


def test_breadth_unavailable_when_quotes_fail(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def _boom(db: Session):
        raise MarketDataUnavailableError("quotes down")

    monkeypatch.setattr(market_breadth, "fetch_market_quotes", _boom)

    body = client.get("/api/v1/market/breadth").json()
    assert body["available"] is False
    assert body["advancers"] == 0
    assert "quotes down" in body["reason"]
