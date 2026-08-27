from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("open", "high", "low", "close", "volume")


def prepare_candles(candles: pd.DataFrame | Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    df = candles.copy() if isinstance(candles, pd.DataFrame) else pd.DataFrame(candles)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"missing candle columns: {', '.join(missing)}")

    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df = df.sort_values("timestamp")

    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    df["volume"] = df["volume"].fillna(0.0).clip(lower=0.0)
    if df.empty:
        raise ValueError("no valid candles")
    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("prices must be positive")
    return df


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)
    avg_gain = gains.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = losses.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    values = 100.0 - (100.0 / (1.0 + rs))
    return values.fillna(50.0)


def true_range(df: pd.DataFrame) -> pd.Series:
    previous_close = df["close"].shift(1)
    ranges = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    return true_range(df).ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def rolling_vwap(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    حساب متوسط السعر المرجح بحجم التداول (Rolling VWAP)
    نستخدم نافذة متحركة (20 يوم افتراضياً) لأن بياناتنا يومية، وهذا يعكس 
    تكلفة الدخول المتوسطة للمؤسسات خلال الشهر الأخير.
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    volume = df["volume"].clip(lower=0.0)

    rolling_vp = (typical_price * volume).rolling(window=window, min_periods=1).sum()
    rolling_vol = volume.rolling(window=window, min_periods=1).sum()

    vwap = rolling_vp / rolling_vol.replace(0.0, pd.NA)
    return vwap.fillna(typical_price)


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["sma_20"] = sma(enriched["close"], 20)
    enriched["sma_50"] = sma(enriched["close"], 50)
    enriched["sma_200"] = sma(enriched["close"], 200)
    enriched["ema_12"] = ema(enriched["close"], 12)
    enriched["ema_26"] = ema(enriched["close"], 26)
    enriched["macd"] = enriched["ema_12"] - enriched["ema_26"]
    enriched["macd_signal"] = ema(enriched["macd"], 9)
    enriched["rsi"] = rsi(enriched["close"])
    enriched["atr"] = atr(enriched)
    enriched["avg_volume_20"] = enriched["volume"].rolling(20, min_periods=5).mean()
    enriched["vwap_20"] = rolling_vwap(enriched, window=20)
    enriched["return_1d"] = enriched["close"].pct_change()
    enriched["return_20d"] = enriched["close"].pct_change(20)
    enriched["volatility_20d"] = enriched["return_1d"].rolling(20, min_periods=10).std()
    return enriched


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return default if not np.isfinite(parsed) else parsed
