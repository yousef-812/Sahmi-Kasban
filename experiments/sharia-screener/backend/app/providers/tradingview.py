import os
from datetime import datetime, timezone

from app.providers.base import MarketDataError
from reusable_data_fetcher import TradingViewConnector, get_tv_symbol


class TradingViewWebSocketProvider:
    """Adapter for the repository's existing TradingViewConnector.

    TradingView's terms restrict automated extraction and non-display algorithmic use.
    This provider stays disabled unless the operator confirms written authorization
    covering this exact use case.
    """
    def __init__(self):
        self.authorized = os.getenv("TRADINGVIEW_DATA_USAGE_AUTHORIZED", "").strip().lower() == "true"

    def daily_candles(self, symbol: str):
        if not self.authorized:
            raise MarketDataError(
                "TradingView WebSocket provider is disabled. Set "
                "TRADINGVIEW_DATA_USAGE_AUTHORIZED=true only if you have permission "
                "covering automated extraction and algorithmic analysis; otherwise use "
                "CSV or a licensed market-data provider."
            )

        import asyncio
        import pandas as pd

        async def fetch():
            connector = TradingViewConnector(
                auth_token=os.getenv("TRADINGVIEW_AUTH_TOKEN", "unauthorized_user_token"),
                timeout_seconds=float(os.getenv("MARKET_DATA_TIMEOUT_SECONDS", "20")),
            )
            try:
                return await connector.get_historical(
                    get_tv_symbol(symbol, "EGX"),
                    timeframe="1D",
                    count=int(os.getenv("MARKET_DATA_CANDLE_COUNT", "300")),
                    timeout=float(os.getenv("MARKET_DATA_TIMEOUT_SECONDS", "20")),
                )
            except Exception as exc:
                raise MarketDataError(f"TradingView WebSocket fetch failed for {symbol}") from exc
            finally:
                await connector.close()

        try:
            rows = asyncio.run(fetch())
        except RuntimeError as exc:
            raise MarketDataError("Unable to create the provider event loop in this context.") from exc
        if not rows:
            raise MarketDataError(f"TradingView returned no historical candles for {symbol}")

        frame = pd.DataFrame(rows)
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        if not required.issubset(frame.columns):
            raise MarketDataError("TradingView response did not contain all OHLCV fields.")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="s", utc=True, errors="coerce")
        for column in ["open", "high", "low", "close", "volume"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["timestamp", "open", "high", "low", "close", "volume"])
        frame = frame.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)
        if len(frame) < 60:
            raise MarketDataError(f"Insufficient usable candles for {symbol}: {len(frame)}")
        return frame
