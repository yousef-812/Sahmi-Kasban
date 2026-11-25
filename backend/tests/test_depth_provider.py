"""WP-26: depth-provider registry wiring and honest degradation."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.market_data import depth as depth_registry
from app.market_data import order_flow
from app.market_data.tradingview_depth import TradingViewDepthProvider
from app.market_data.types import (
    DEPTH_CAP_DEPTH,
    DEPTH_CAP_ORDER_BOOK,
    DEPTH_CAP_TRADES,
    DepthLevel,
    DepthSummaryData,
    MarketDataUnavailableError,
    OrderBookData,
    RecentTradeData,
    RecentTradeItem,
)

AS_OF = datetime(2026, 10, 15, 11, 0, tzinfo=UTC)
NO_PROVIDER_REASON = "No depth-capable market-data provider is configured"


class _FakeDepthProvider:
    name = "fake"
    capabilities = frozenset({DEPTH_CAP_ORDER_BOOK, DEPTH_CAP_TRADES, DEPTH_CAP_DEPTH})

    async def get_order_book(self, ticker: str, *, levels: int = 10) -> OrderBookData:
        return OrderBookData(
            ticker=ticker,
            provider=self.name,
            as_of=AS_OF,
            bids=(
                DepthLevel(price=99.0, size=1_200.0),
                DepthLevel(price=98.5, size=900.0),
            ),
            asks=(DepthLevel(price=100.0, size=800.0),),
        )

    async def get_recent_trades(self, ticker: str, *, limit: int = 200) -> RecentTradeData:
        return RecentTradeData(
            ticker=ticker,
            provider=self.name,
            items=(
                RecentTradeItem(
                    price=99.5,
                    size=100.0,
                    turnover_egp=9_950.0,
                    side="buy",
                    executed_at=AS_OF,
                ),
            ),
        )

    async def get_market_depth(self, ticker: str, *, levels: int = 10) -> DepthSummaryData:
        return DepthSummaryData(
            ticker=ticker,
            provider=self.name,
            as_of=AS_OF,
            levels=levels,
            bid_levels=(DepthLevel(price=99.0, size=1_200.0),),
            ask_levels=(DepthLevel(price=100.0, size=800.0),),
            spread=1.0,
            mid_price=99.5,
        )


class _TradesOnlyProvider(_FakeDepthProvider):
    capabilities = frozenset({DEPTH_CAP_TRADES})


class _BrokenOrderBookProvider(_FakeDepthProvider):
    async def get_order_book(self, ticker: str, *, levels: int = 10) -> OrderBookData:
        raise MarketDataUnavailableError("depth feed down")


def test_registry_returns_none_for_disabled_or_unknown_names() -> None:
    assert depth_registry._depth_provider_from_name("none") is None
    assert depth_registry._depth_provider_from_name("  ") is None
    assert depth_registry._depth_provider_from_name("unknown-feed") is None


def test_registry_builds_tradingview_skeleton_without_capabilities() -> None:
    provider = depth_registry._depth_provider_from_name("tradingview")

    assert isinstance(provider, TradingViewDepthProvider)
    assert provider.capabilities == frozenset()
    assert not depth_registry.supports(provider, DEPTH_CAP_ORDER_BOOK)


def test_supports_handles_none_provider() -> None:
    assert not depth_registry.supports(None, DEPTH_CAP_ORDER_BOOK)


def test_default_registry_returns_none_and_getters_report_unavailable(
    db_session,
) -> None:
    depth_registry.get_depth_provider.cache_clear()

    book = asyncio.run(order_flow.get_order_book(db_session, "comi"))
    assert book["available"] is False
    assert book["provider"] is None
    assert book["reason"] == NO_PROVIDER_REASON
    assert book["bids"] == [] and book["asks"] == []

    trades = asyncio.run(order_flow.get_recent_trades(db_session, "comi"))
    assert trades["available"] is False
    assert trades["reason"] == NO_PROVIDER_REASON
    assert trades["items"] == []

    depth = asyncio.run(order_flow.get_market_depth(db_session, "comi", levels=5))
    assert depth["available"] is False
    assert depth["reason"] == NO_PROVIDER_REASON
    assert depth["levels"] == 5


def test_capable_provider_passes_data_through(db_session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(order_flow, "get_depth_provider", lambda: _FakeDepthProvider())

    book = asyncio.run(order_flow.get_order_book(db_session, "comi"))
    assert book["available"] is True
    assert book["provider"] == "fake"
    assert book["reason"] is None
    assert book["bids"] == [{"price": 99.0, "size": 1200.0}, {"price": 98.5, "size": 900.0}]
    assert book["asks"] == [{"price": 100.0, "size": 800.0}]
    assert book["as_of"] == AS_OF

    trades = asyncio.run(order_flow.get_recent_trades(db_session, "comi", limit=10))
    assert trades["available"] is True
    assert trades["provider"] == "fake"
    assert len(trades["items"]) == 1
    assert trades["items"][0]["price"] == 99.5
    assert trades["items"][0]["turnover_egp"] == 9_950.0

    depth = asyncio.run(order_flow.get_market_depth(db_session, "comi", levels=5))
    assert depth["available"] is True
    assert depth["provider"] == "fake"
    assert depth["total_bid_volume"] == 1_200.0
    assert depth["total_ask_volume"] == 800.0
    assert depth["spread"] == 1.0
    assert depth["mid_price"] == 99.5


def test_provider_without_capability_reports_reason(db_session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(order_flow, "get_depth_provider", lambda: _TradesOnlyProvider())

    book = asyncio.run(order_flow.get_order_book(db_session, "comi"))
    assert book["available"] is False
    assert book["reason"] == "Provider 'fake' does not support 'order_book'"

    trades = asyncio.run(order_flow.get_recent_trades(db_session, "comi"))
    assert trades["available"] is True
    assert trades["provider"] == "fake"


def test_provider_failure_degrades_to_reason(db_session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(order_flow, "get_depth_provider", lambda: _BrokenOrderBookProvider())

    book = asyncio.run(order_flow.get_order_book(db_session, "comi"))
    assert book["available"] is False
    assert book["reason"] == "depth feed down"
    assert book["bids"] == []


def test_tradingview_skeleton_methods_raise_unavailable() -> None:
    provider = TradingViewDepthProvider()

    with pytest.raises(MarketDataUnavailableError):
        asyncio.run(provider.get_order_book("COMI"))
    with pytest.raises(MarketDataUnavailableError):
        asyncio.run(provider.get_recent_trades("COMI"))
    with pytest.raises(MarketDataUnavailableError):
        asyncio.run(provider.get_market_depth("COMI"))


def test_settings_accepts_known_depth_providers_and_rejects_unknown() -> None:
    assert Settings(_env_file=None, market_data_depth_provider="none").market_data_depth_provider == "none"
    assert (
        Settings(_env_file=None, market_data_depth_provider="TradingView").market_data_depth_provider
        == "TradingView"
    )

    with pytest.raises(ValidationError, match="MARKET_DATA_DEPTH_PROVIDER"):
        Settings(_env_file=None, market_data_depth_provider="polygons")
