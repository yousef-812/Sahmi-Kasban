"""TradingView depth provider skeleton (WP-26) — capability wiring only.

Reality: the TradingView feed wired in this repo (``reusable_data_fetcher.py``)
exposes top-of-book bid/ask prices without sizes, no L2 ladder, and no
time-and-sales feed for EGX on the free tier. This provider is therefore
*registered but capability-empty*: ``capabilities`` is ``frozenset()``, so
``order_flow`` never calls its methods and keeps reporting ``available: false``.

Future work (licensed depth source or a free-EGX integration): implement the
three methods below and add the matching ``DEPTH_CAP_*`` constants to
``capabilities`` — no changes will be needed in ``order_flow``, the response
schemas, the routes, or the Flutter layer.
"""

from __future__ import annotations

from app.market_data.types import (
    DepthProvider,
    DepthSummaryData,
    MarketDataUnavailableError,
    OrderBookData,
    RecentTradeData,
)

_NO_LADDER_MESSAGE = "TradingView feed has no L2 ladder for EGX without a licensed depth source"


class TradingViewDepthProvider:
    """Skeleton depth provider — zero capabilities until a real feed lands."""

    name = "tradingview"
    capabilities: frozenset[str] = frozenset()

    async def get_order_book(
        self,
        ticker: str,
        *,
        levels: int = 10,
    ) -> OrderBookData:
        raise MarketDataUnavailableError(_NO_LADDER_MESSAGE)

    async def get_recent_trades(
        self,
        ticker: str,
        *,
        limit: int = 200,
    ) -> RecentTradeData:
        raise MarketDataUnavailableError(_NO_LADDER_MESSAGE)

    async def get_market_depth(
        self,
        ticker: str,
        *,
        levels: int = 10,
    ) -> DepthSummaryData:
        raise MarketDataUnavailableError(_NO_LADDER_MESSAGE)


def build_tradingview_depth_provider() -> DepthProvider:
    return TradingViewDepthProvider()
