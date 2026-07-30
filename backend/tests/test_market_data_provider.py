import asyncio
from datetime import UTC, datetime

import pandas as pd
import pytest

from app.market_data.egx_symbols import normalize_egx_ticker, to_yahoo_symbol
from app.market_data.provider import FallbackMarketDataProvider, YFinanceMarketDataProvider
from app.market_data.tradingview import _normalize_candles
from app.market_data.types import (
    CandleSeries,
    MarketDataUnavailableError,
    UnknownTickerError,
)


def test_egx_ticker_normalization_and_yahoo_mapping() -> None:
    assert normalize_egx_ticker(" comi.ca ") == "COMI"
    assert to_yahoo_symbol("comi") == "COMI.CA"
    with pytest.raises(UnknownTickerError):
        normalize_egx_ticker("NOT-A-TICKER")


def test_yfinance_frame_normalization_rejects_invalid_rows() -> None:
    index = pd.DatetimeIndex(
        [
            datetime(2026, 7, 22, tzinfo=UTC),
            datetime(2026, 7, 23, tzinfo=UTC),
            datetime(2026, 7, 24, tzinfo=UTC),
        ]
    )
    frame = pd.DataFrame(
        {
            "Open": [10.0, 11.0, 12.0],
            "High": [11.0, 10.0, 13.0],
            "Low": [9.0, 10.5, 11.0],
            "Close": [10.5, 11.5, 12.5],
            "Volume": [1000, 2000, -50],
        },
        index=index,
    )

    candles = YFinanceMarketDataProvider._normalize_frame(frame)
    assert len(candles) == 2
    assert candles[0]["close"] == 10.5
    assert candles[1]["volume"] == 0.0
    assert str(candles[1]["timestamp"]).endswith("+00:00")


def test_tradingview_normalization_accepts_short_valid_history() -> None:
    candles = _normalize_candles(
        [
            {
                "timestamp": 1_753_228_800,
                "open": 10,
                "high": 11,
                "low": 9,
                "close": 10.5,
                "volume": 1_000,
            },
            {
                "timestamp": 1_753_315_200,
                "open": 10.5,
                "high": 10,
                "low": 9.5,
                "close": 10.2,
                "volume": 1_100,
            },
        ]
    )

    assert len(candles) == 1
    assert candles[0]["close"] == 10.5


class _FlakyProvider:
    name = "flaky"

    def __init__(self, *, succeeds_on: int | None) -> None:
        self.succeeds_on = succeeds_on
        self.calls = 0

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        if self.succeeds_on is None or self.calls < self.succeeds_on:
            raise MarketDataUnavailableError(f"temporary failure {self.calls}")
        now = datetime.now(UTC)
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=now,
            data_as_of=now,
            fingerprint="f" * 64,
            candles=(
                {
                    "timestamp": now.isoformat(),
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.0,
                    "close": 10.5,
                    "volume": 1000.0,
                },
            ),
        )


def test_fallback_provider_retries_transient_failure_before_fallback() -> None:
    primary = _FlakyProvider(succeeds_on=2)
    fallback = _FlakyProvider(succeeds_on=1)
    provider = FallbackMarketDataProvider(
        (primary, fallback),
        retry_attempts=2,
        retry_backoff_seconds=0,
    )

    series = asyncio.run(provider.get_history("COMI", period="1y", interval="1d"))

    assert series.provider == "flaky"
    assert primary.calls == 2
    assert fallback.calls == 0


def test_fallback_provider_moves_on_after_bounded_retries() -> None:
    primary = _FlakyProvider(succeeds_on=None)
    fallback = _FlakyProvider(succeeds_on=1)
    provider = FallbackMarketDataProvider(
        (primary, fallback),
        retry_attempts=2,
        retry_backoff_seconds=0,
    )

    series = asyncio.run(provider.get_history("COMI", period="1y", interval="1d"))

    assert series.provider == "flaky"
    assert primary.calls == 2
    assert fallback.calls == 1
