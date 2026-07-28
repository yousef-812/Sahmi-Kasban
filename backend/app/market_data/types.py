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
