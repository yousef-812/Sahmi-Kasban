from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class MarketDataError(RuntimeError):
    """Base error for market-data operations."""


class UnknownTickerError(MarketDataError):
    """Raised when a ticker is outside the supported EGX catalog."""


class MarketDataUnavailableError(MarketDataError):
    """Raised when configured providers cannot return usable candles."""


@dataclass(frozen=True, slots=True)
class MarketInstrument:
    ticker: str
    provider_symbol: str
    exchange: str = "EGX"
    description: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "ticker": self.ticker,
            "provider_symbol": self.provider_symbol,
            "exchange": self.exchange,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class CandleSeries:
    ticker: str
    provider: str
    interval: str
    period: str
    fetched_at: datetime
    data_as_of: datetime
    fingerprint: str
    candles: tuple[dict[str, object], ...]

    @property
    def candle_count(self) -> int:
        return len(self.candles)

    def to_payload(self) -> dict[str, object]:
        return {
            "ticker": self.ticker,
            "provider": self.provider,
            "interval": self.interval,
            "period": self.period,
            "fetched_at": self.fetched_at.isoformat(),
            "data_as_of": self.data_as_of.isoformat(),
            "fingerprint": self.fingerprint,
            "candles": list(self.candles),
        }


class MarketDataProvider(Protocol):
    name: str

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        """Return normalized OHLCV candles for a supported EGX ticker."""


DEPTH_CAP_ORDER_BOOK = "order_book"
DEPTH_CAP_TRADES = "trades"
DEPTH_CAP_DEPTH = "depth"
DEPTH_CAP_TOP_OF_BOOK = "top_of_book"


@dataclass(frozen=True, slots=True)
class DepthLevel:
    price: float
    size: float

    def to_dict(self) -> dict[str, float]:
        return {"price": self.price, "size": self.size}


@dataclass(frozen=True, slots=True)
class OrderBookData:
    ticker: str
    provider: str
    as_of: datetime | None
    bids: tuple[DepthLevel, ...]
    asks: tuple[DepthLevel, ...]


@dataclass(frozen=True, slots=True)
class RecentTradeItem:
    price: float
    size: float
    turnover_egp: float
    side: str = "unknown"
    executed_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "executed_at": self.executed_at,
            "price": self.price,
            "size": self.size,
            "turnover_egp": self.turnover_egp,
            "side": self.side,
        }


@dataclass(frozen=True, slots=True)
class RecentTradeData:
    ticker: str
    provider: str
    items: tuple[RecentTradeItem, ...]


@dataclass(frozen=True, slots=True)
class DepthSummaryData:
    ticker: str
    provider: str
    as_of: datetime | None
    levels: int
    bid_levels: tuple[DepthLevel, ...]
    ask_levels: tuple[DepthLevel, ...]
    spread: float | None
    mid_price: float | None

    @property
    def total_bid_volume(self) -> float:
        return sum(level.size for level in self.bid_levels)

    @property
    def total_ask_volume(self) -> float:
        return sum(level.size for level in self.ask_levels)


class DepthProvider(Protocol):
    """Level-2 depth feed — independent of the candles ``MarketDataProvider``.

    A provider advertises only the feed kinds it truly supports via
    ``capabilities`` (constants ``DEPTH_CAP_*``). Consumers must check
    the capability before calling the matching method, and implementations
    of unsupported methods should raise ``MarketDataUnavailableError``.
    """

    name: str
    capabilities: frozenset[str]

    async def get_order_book(
        self,
        ticker: str,
        *,
        levels: int = 10,
    ) -> OrderBookData:
        """Return the level-2 order book (bids/asks ladder)."""

    async def get_recent_trades(
        self,
        ticker: str,
        *,
        limit: int = 200,
    ) -> RecentTradeData:
        """Return the most recent executed trades (time & sales)."""

    async def get_market_depth(
        self,
        ticker: str,
        *,
        levels: int = 10,
    ) -> DepthSummaryData:
        """Return an aggregated market-depth summary."""
