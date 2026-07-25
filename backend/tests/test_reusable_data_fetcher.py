from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from reusable_data_fetcher import (
    StockDataFetcher,
    TechnicalAnalysisService,
    TradingViewConnector,
    _parse_symbol,
    _provider_symbols,
)


def _sample_candles(count: int = 240) -> list[dict[str, float | int]]:
    start = datetime(2025, 1, 1, tzinfo=UTC)
    candles: list[dict[str, float | int]] = []
    for index in range(count):
        close = 40 + (index * 0.08) + ((index % 9) * 0.03)
        candles.append(
            {
                "timestamp": int((start + timedelta(days=index)).timestamp()),
                "open": close - 0.15,
                "high": close + 0.45,
                "low": close - 0.50,
                "close": close,
                "volume": 500_000 + (index * 1000),
            }
        )
    return candles


def test_market_symbol_mapping_supports_direct_and_explicit_formats() -> None:
    assert _parse_symbol("COMI", "EGX") == ("EGX", "COMI")
    assert _parse_symbol("EGX:COMI", "US") == ("EGX", "COMI")
    assert _provider_symbols("COMI", "EGX") == ("EGX:COMI", "COMI.CA")
    assert _provider_symbols("AAPL", "US") == ("NASDAQ:AAPL", "AAPL")
    assert _provider_symbols("VOD", "LSE") == ("LSE:VOD", "VOD.L")


def test_tradingview_history_normalization_filters_and_deduplicates() -> None:
    points = [
        {"v": [1_700_000_000, 10, 12, 9, 11, 1000]},
        {"v": [1_700_086_400, 11, 13, 10, 12, 1200]},
        {"v": [1_700_086_400, 11.5, 13.5, 10.5, 13, 1400]},
        {"v": [1_700_172_800, 12, 11, 10, 13, 1600]},
    ]
    candles = TradingViewConnector._normalize_history(points)
    assert len(candles) == 2
    assert candles[0]["close"] == 11.0
    assert candles[1]["close"] == 13.0
    assert candles[1]["volume"] == 1400.0


def test_technical_indicators_are_calculated_from_candles() -> None:
    indicators = TechnicalAnalysisService.calculate_indicators(_sample_candles())
    assert indicators["price"] > 0
    assert indicators["sma_20"] is not None
    assert indicators["sma_50"] is not None
    assert indicators["sma_200"] is not None
    assert indicators["rsi"] is not None
    assert indicators["macd"] is not None
    assert indicators["bb_upper"] is not None
    assert indicators["atr"] is not None
    assert indicators["trend"] in {"UPTREND", "DOWNTREND", "SIDEWAYS"}


def test_full_data_uses_historical_price_when_realtime_fails() -> None:
    fetcher = StockDataFetcher()
    candles = _sample_candles()

    async def failing_realtime(symbol: str, market: str = "EGX") -> dict:
        raise TimeoutError(f"no realtime quote for {market}:{symbol}")

    async def fake_history(
        symbol: str,
        market: str = "EGX",
        timeframe: str = "1D",
        count: int = 200,
    ) -> list[dict]:
        assert symbol == "COMI"
        assert market == "EGX"
        assert timeframe == "1D"
        assert count == 200
        return candles

    def fake_fundamentals(symbol: str, market: str = "EGX") -> dict:
        return {"company_name": "Commercial International Bank"}

    fetcher.get_realtime_price = failing_realtime
    fetcher.get_historical_data = fake_history
    fetcher.get_fundamentals = fake_fundamentals

    async def run() -> dict:
        try:
            return await fetcher.get_full_data("EGX:COMI")
        finally:
            await fetcher.close()

    result = asyncio.run(run())
    assert result["symbol"] == "COMI"
    assert result["market"] == "EGX"
    assert result["price"]["source"] == "historical_fallback"
    assert result["price"]["price"] == candles[-1]["close"]
    assert len(result["historical"]) == 240
    assert result["indicators"]["rsi"] is not None
    assert result["fundamentals"]["company_name"].startswith("Commercial")
