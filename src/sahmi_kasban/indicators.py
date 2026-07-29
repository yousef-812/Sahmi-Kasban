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


def adx(df: pd.DataFrame, window: int = 14) -> pd.Series:
    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=df.index,
        dtype=float,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=df.index,
        dtype=float,
    )
    average_range = atr(df, window).replace(0.0, np.nan)
    plus_di = 100.0 * plus_dm.ewm(
        alpha=1 / window,
        adjust=False,
        min_periods=window,
    ).mean() / average_range
    minus_di = 100.0 * minus_dm.ewm(
        alpha=1 / window,
        adjust=False,
        min_periods=window,
    ).mean() / average_range
    denominator = (plus_di + minus_di).replace(0.0, np.nan)
    dx = ((plus_di - minus_di).abs() / denominator) * 100.0
    return dx.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def _log_slope_pct(values: np.ndarray) -> float:
    cleaned = np.asarray(values, dtype=float)
    if len(cleaned) < 3 or not np.isfinite(cleaned).all() or (cleaned <= 0).any():
        return 0.0
    x = np.arange(len(cleaned), dtype=float)
    slope = np.polyfit(x, np.log(cleaned), 1)[0]
    return float(np.expm1(slope) * 100.0)


def _trend_r_squared(values: np.ndarray) -> float:
    cleaned = np.asarray(values, dtype=float)
    if len(cleaned) < 3 or not np.isfinite(cleaned).all() or (cleaned <= 0).any():
        return 0.0
    x = np.arange(len(cleaned), dtype=float)
    y = np.log(cleaned)
    coefficients = np.polyfit(x, y, 1)
    predicted = np.polyval(coefficients, x)
    residual = float(np.square(y - predicted).sum())
    total = float(np.square(y - y.mean()).sum())
    return 0.0 if total <= 0 else max(0.0, min(1.0, 1.0 - residual / total))


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["sma_20"] = sma(enriched["close"], 20)
    enriched["sma_50"] = sma(enriched["close"], 50)
    enriched["sma_200"] = sma(enriched["close"], 200)
    enriched["ema_12"] = ema(enriched["close"], 12)
    enriched["ema_26"] = ema(enriched["close"], 26)
    enriched["macd"] = enriched["ema_12"] - enriched["ema_26"]
    enriched["macd_signal"] = ema(enriched["macd"], 9)
    enriched["macd_histogram"] = enriched["macd"] - enriched["macd_signal"]
    enriched["rsi"] = rsi(enriched["close"])
    enriched["atr"] = atr(enriched)
    enriched["atr_pct"] = enriched["atr"] / enriched["close"] * 100.0
    enriched["adx_14"] = adx(enriched)
    enriched["avg_volume_20"] = enriched["volume"].rolling(20, min_periods=5).mean()
    enriched["volume_ratio"] = enriched["volume"] / enriched["avg_volume_20"].replace(
        0.0,
        np.nan,
    )
    enriched["return_1d"] = enriched["close"].pct_change()
    enriched["return_5d"] = enriched["close"].pct_change(5)
    enriched["return_20d"] = enriched["close"].pct_change(20)
    enriched["return_60d"] = enriched["close"].pct_change(60)
    enriched["volatility_20d"] = enriched["return_1d"].rolling(20, min_periods=10).std()
    enriched["volatility_60d"] = enriched["return_1d"].rolling(60, min_periods=20).std()
    rolling_peak = enriched["close"].rolling(60, min_periods=10).max()
    enriched["drawdown_60d"] = enriched["close"] / rolling_peak - 1.0
    rolling_std = enriched["close"].rolling(20, min_periods=20).std()
    enriched["bollinger_bandwidth"] = 4.0 * rolling_std / enriched["sma_20"].replace(
        0.0,
        np.nan,
    )
    absolute_path = enriched["close"].diff().abs().rolling(20, min_periods=10).sum()
    enriched["price_efficiency_20"] = (
        enriched["close"].diff(20).abs() / absolute_path.replace(0.0, np.nan)
    )
    enriched["trend_slope_20"] = enriched["close"].rolling(20, min_periods=20).apply(
        _log_slope_pct,
        raw=True,
    )
    enriched["trend_r2_20"] = enriched["close"].rolling(20, min_periods=20).apply(
        _trend_r_squared,
        raw=True,
    )
    enriched["trend_slope_60"] = enriched["close"].rolling(60, min_periods=40).apply(
        _log_slope_pct,
        raw=True,
    )
    enriched["trend_r2_60"] = enriched["close"].rolling(60, min_periods=40).apply(
        _trend_r_squared,
        raw=True,
    )
    numeric_columns = enriched.select_dtypes(include=["number"]).columns
    enriched[numeric_columns] = enriched[numeric_columns].replace([np.inf, -np.inf], np.nan)
    return enriched


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return default if not np.isfinite(parsed) else parsed
