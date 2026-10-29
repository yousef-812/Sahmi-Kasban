from abc import ABC, abstractmethod
import pandas as pd


class MarketDataError(RuntimeError):
    """Raised when market data is unavailable, stale, or malformed."""


class MarketDataProvider(ABC):
    @abstractmethod
    def daily_candles(self, symbol: str) -> pd.DataFrame:
        """Return timestamp/open/high/low/close/volume daily candles."""
        raise NotImplementedError


class CSVProvider(MarketDataProvider):
    def __init__(self, data_dir: str = "data"):
        from pathlib import Path
        self.data_dir = Path(data_dir)

    def daily_candles(self, symbol: str) -> pd.DataFrame:
        path = self.data_dir / f"{symbol.replace(':', '_')}.csv"
        if not path.exists():
            raise MarketDataError(
                f"No local candle file for {symbol}. Configure a licensed provider "
                "or add daily OHLCV CSV data."
            )
        frame = pd.read_csv(path)
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        missing = required - set(frame.columns)
        if missing:
            raise MarketDataError(f"Missing columns for {symbol}: {sorted(missing)}")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
        frame = frame.dropna(subset=["timestamp", "open", "high", "low", "close", "volume"])
        frame = frame.sort_values("timestamp").drop_duplicates("timestamp")
        if len(frame) < 60:
            raise MarketDataError(f"Insufficient candles for {symbol}: {len(frame)}; need at least 60.")
        return frame.reset_index(drop=True)
