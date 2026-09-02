from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta

import websockets

from reusable_data_fetcher import (
    StockDataFetcher,
    TechnicalAnalysisService,
    TradingViewConnector,
    get_tv_symbol,
    get_yf_symbol,
    parse_symbol,
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


def test_market_symbol_mapping_supports_all_requested_formats() -> None:
    assert parse_symbol("COMI", "EGX") == ("EGX", "COMI")
    assert parse_symbol("EGX:COMI", "US") == ("EGX", "COMI")
    assert get_tv_symbol("COMI", "EGX") == "EGX:COMI"
    assert get_yf_symbol("COMI", "EGX") == "COMI.CA"
    assert get_tv_symbol("AAPL", "US") == "NASDAQ:AAPL"
    assert get_yf_symbol("AAPL", "US") == "AAPL"
    assert get_tv_symbol("VOD", "LSE") == "LON:VOD"
    assert get_yf_symbol("VOD", "LSE") == "VOD.L"
    assert get_tv_symbol("2222", "TADAWUL") == "TADAWUL:2222"
    assert get_yf_symbol("2222", "TADAWUL") == "2222.SR"


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
    service = TechnicalAnalysisService()
    frame = service.calculate_all_indicators(__import__("pandas").DataFrame(_sample_candles()))
    indicators = service.get_current_indicators(frame)
    assert indicators["price"] > 0
    assert indicators["sma_20"] is not None
    assert indicators["sma_50"] is not None
    assert indicators["sma_200"] is not None
    assert indicators["rsi"] is not None
    assert indicators["macd"] is not None
    assert indicators["bb_upper"] is not None
    assert indicators["atr"] is not None


def test_full_data_uses_historical_price_when_realtime_is_unavailable() -> None:
    fetcher = StockDataFetcher()
    candles = _sample_candles()

    async def unavailable_realtime(symbol: str, market: str = "EGX") -> dict:
        return {
            "symbol": symbol,
            "market": market,
            "price": None,
            "source": "unavailable",
        }

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

    fetcher.get_realtime_price = unavailable_realtime
    fetcher.get_historical_data = fake_history
    fetcher.get_fundamentals = fake_fundamentals

    async def run() -> dict:
        try:
            return await fetcher.get_full_data("EGX:COMI")
        finally:
            await fetcher.close()

    result = asyncio.run(run())
    assert result["ticker"] == "COMI"
    assert result["market"] == "EGX"
    assert result["price"]["source"] == "historical_fallback"
    assert result["price"]["price"] == candles[-1]["close"]
    assert len(result["historical"]) == 240
    assert result["indicators"]["rsi"] is not None
    assert result["fundamentals"]["company_name"].startswith("Commercial")
    assert result["errors"] == []


def test_custom_token_heartbeat_and_full_facade_with_local_websocket(monkeypatch) -> None:
    received_tokens: list[str] = []
    heartbeat_echoes: list[str] = []

    def frame(payload: dict) -> str:
        encoded = json.dumps(payload, separators=(",", ":"))
        return f"~m~{len(encoded)}~m~{encoded}"

    async def handler(websocket) -> None:
        heartbeat_sent = False
        async for raw in websocket:
            if raw == "~m~6~m~~h~123":
                heartbeat_echoes.append(raw)
                continue
            for message in TradingViewConnector._parse(raw):
                method = message.get("m")
                params = message.get("p", [])
                if method == "set_auth_token":
                    received_tokens.append(params[0])
                    if not heartbeat_sent:
                        await websocket.send("~m~6~m~~h~123")
                        heartbeat_sent = True
                elif method == "quote_add_symbols":
                    symbol = params[1]
                    await websocket.send(
                        frame(
                            {
                                "m": "qsd",
                                "p": [
                                    params[0],
                                    {
                                        "n": symbol,
                                        "s": "ok",
                                        "v": {
                                            "lp": 72.5,
                                            "ch": 1.0,
                                            "chp": 1.4,
                                            "v": 1_000_000,
                                            "open_price": 71.5,
                                        },
                                    },
                                ],
                            }
                        )
                    )
                elif method == "create_series":
                    chart_session, series_name = params[0], params[1]
                    points = []
                    for index in range(200):
                        close = 50 + index * 0.1
                        points.append(
                            {
                                "v": [
                                    1_700_000_000 + index * 86_400,
                                    close - 0.2,
                                    close + 0.5,
                                    close - 0.5,
                                    close,
                                    100_000 + index,
                                ]
                            }
                        )
                    await websocket.send(
                        frame(
                            {
                                "m": "timescale_update",
                                "p": [
                                    chart_session,
                                    {series_name: {"s": points}},
                                ],
                            }
                        )
                    )

    async def run() -> dict:
        server = await websockets.serve(handler, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        monkeypatch.setattr(
            TradingViewConnector,
            "URL",
            f"ws://127.0.0.1:{port}",
        )
        fetcher = StockDataFetcher(tv_token="CUSTOM_TOKEN", pool_size=2)
        fetcher.calculate_indicators = lambda candles: {"rsi": 55.0}
        fetcher.get_fundamentals = lambda symbol, market="EGX": {"pe_ratio": 7.5}
        try:
            result = await fetcher.get_full_data("COMI", market="EGX")
            await asyncio.sleep(0.05)
            return result
        finally:
            await fetcher.close()
            server.close()
            await server.wait_closed()

    result = asyncio.run(run())
    assert received_tokens == ["CUSTOM_TOKEN", "CUSTOM_TOKEN"]
    assert len(heartbeat_echoes) == 2
    assert result["ticker"] == "COMI"
    assert result["price"]["price"] == 72.5
    assert len(result["historical"]) == 200
    assert result["indicators"]["rsi"] == 55.0
    assert result["fundamentals"]["pe_ratio"] == 7.5
    assert result["errors"] == []
