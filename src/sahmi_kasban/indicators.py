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


def stochastic(
    df: pd.DataFrame, k_window: int = 14, d_window: int = 3
) -> tuple[pd.Series, pd.Series]:
    lowest_low = df["low"].rolling(window=k_window, min_periods=k_window).min()
    highest_high = df["high"].rolling(window=k_window, min_periods=k_window).max()
    spread = (highest_high - lowest_low).replace(0.0, np.nan)
    fast_k = 100.0 * (df["close"] - lowest_low) / spread
    slow_d = fast_k.rolling(window=d_window, min_periods=d_window).mean()
    return fast_k.fillna(50.0), slow_d.fillna(50.0)


def adx(df: pd.DataFrame, window: int = 14) -> tuple[pd.Series, pd.Series, pd.Series]:
    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = ((up_move > down_move) & (up_move > 0.0)).astype(float) * up_move.fillna(0.0)
    minus_dm = ((down_move > up_move) & (down_move > 0.0)).astype(float) * down_move.fillna(0.0)
    alpha = 1 / window
    smoothed_tr = true_range(df).ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    smoothed_plus = plus_dm.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    smoothed_minus = minus_dm.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    denominator = smoothed_tr.replace(0.0, np.nan)
    plus_di = (100.0 * smoothed_plus / denominator).fillna(0.0)
    minus_di = (100.0 * smoothed_minus / denominator).fillna(0.0)
    di_sum = (plus_di + minus_di).replace(0.0, np.nan)
    dx = (100.0 * (plus_di - minus_di).abs() / di_sum).fillna(0.0)
    adx_value = dx.ewm(alpha=alpha, adjust=False, min_periods=window).mean().fillna(0.0)
    return adx_value, plus_di, minus_di


def bollinger(
    close: pd.Series, window: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    middle = close.rolling(window=window, min_periods=window).mean()
    deviation = close.rolling(window=window, min_periods=window).std(ddof=0)
    upper = middle + num_std * deviation
    lower = middle - num_std * deviation
    return upper, middle, lower


def mfi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    raw_flow = typical_price * df["volume"]
    delta = typical_price.diff()
    positive = raw_flow.where(delta > 0.0, 0.0).rolling(window=window, min_periods=window).sum()
    negative = raw_flow.where(delta < 0.0, 0.0).rolling(window=window, min_periods=window).sum()
    total = (positive + negative).replace(0.0, np.nan)
    return (100.0 * positive / total).fillna(50.0)


def obv(df: pd.DataFrame) -> pd.Series:
    direction = np.sign(df["close"].diff().fillna(0.0))
    return (df["volume"] * direction).cumsum()


def obv_trend(df: pd.DataFrame, window: int = 20) -> int:
    series = obv(df)
    if len(series) < 2:
        return 0
    span = min(window, len(series) - 1)
    start = safe_float(series.iloc[-1 - span])
    end = safe_float(series.iloc[-1])
    if end > start:
        return 1
    if end < start:
        return -1
    return 0


def close_location_value(df: pd.DataFrame) -> pd.Series:
    """CLV: موقع الإغلاق داخل مدى الشمعة، ‎[-1, 1]‎ (0 عند مدى صفري)."""
    bar_range = (df["high"] - df["low"]).replace(0.0, np.nan)
    clv = ((2.0 * df["close"]) - df["high"] - df["low"]) / bar_range
    return clv.fillna(0.0).clip(-1.0, 1.0)


def buy_sell_volume(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """توزيع حجم كل شمعة بين المشترين والبائعين بأوزان CLV."""
    weight = close_location_value(df)
    buy = df["volume"] * weight.clip(lower=0.0)
    sell = df["volume"] * (-weight).clip(lower=0.0)
    return buy.astype(float), sell.astype(float)


def accumulation_distribution(df: pd.DataFrame) -> pd.Series:
    """خط التراكم/التوزيع: مجموع الحجم المرجّح بموقع الإغلاق (CLV)."""
    return (df["volume"] * close_location_value(df)).cumsum()


def ad_trend(df: pd.DataFrame, window: int = 20) -> int:
    """اتجاه خط A/D خلال ``window`` جلسة: ‎+1‎ تراكم، ‎-1‎ توزيع، ‎0‎ محايد."""
    series = accumulation_distribution(df)
    if len(series) < 2:
        return 0
    span = min(window, len(series) - 1)
    start = safe_float(series.iloc[-1 - span])
    end = safe_float(series.iloc[-1])
    if end > start:
        return 1
    if end < start:
        return -1
    return 0


def flow_summary(df: pd.DataFrame, window: int = 20) -> dict[str, object]:
    """ملخّص ضغط الشراء/البيع من OHLCV — تقدير لا أوامر فعلية.

    الحجم يُقسَّم بين المشترين/البائعين بأوزان CLV داخل آخر ``window`` جلسة.
    عتبات الحكم على ``verdict``: حصة المشترين ‎>= 55%‎ → ``accumulate``،
    ‎<= 45%‎ → ``distribute``، وما بينهما ``neutral``.
    """
    buy, sell = buy_sell_volume(df)
    span = min(window, len(df))
    total_buy = safe_float(buy.tail(span).sum())
    total_sell = safe_float(sell.tail(span).sum())
    total = total_buy + total_sell
    buy_share = round(100.0 * total_buy / total, 4) if total > 0 else 50.0
    sell_share = round(100.0 * total_sell / total, 4) if total > 0 else 50.0
    if buy_share >= 55.0:
        verdict = "accumulate"
    elif buy_share <= 45.0:
        verdict = "distribute"
    else:
        verdict = "neutral"
    return {
        "buy_volume": round(total_buy, 2),
        "sell_volume": round(total_sell, 2),
        "buy_share_pct": buy_share,
        "sell_share_pct": sell_share,
        "net_volume": round(total_buy - total_sell, 2),
        "ad_trend": ad_trend(df, window=span),
        "mfi14": round(safe_float(mfi(df).iloc[-1], 50.0), 4),
        "obv_trend": obv_trend(df, window=span),
        "verdict": verdict,
    }


def relative_volume(df: pd.DataFrame, window: int = 20) -> pd.Series:
    average = df["volume"].rolling(window=window, min_periods=5).mean()
    return (df["volume"] / average.replace(0.0, np.nan)).fillna(1.0)


def performance_pct(close: pd.Series, periods: int) -> pd.Series:
    reference = close.shift(periods)
    return ((close / reference) - 1.0) * 100.0


def high_52w(close: pd.Series, window: int = 252) -> float:
    return safe_float(close.tail(window).max())


def low_52w(close: pd.Series, window: int = 252) -> float:
    return safe_float(close.tail(window).min())


def breakout_flag(close: pd.Series, window: int = 20) -> pd.Series:
    ceiling = close.rolling(window=window, min_periods=window).max().shift(1)
    return (close > ceiling).astype(float)


def breakdown_flag(close: pd.Series, window: int = 20) -> pd.Series:
    floor = close.rolling(window=window, min_periods=window).min().shift(1)
    return (close < floor).astype(float)


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
    bb_upper, bb_middle, bb_lower = bollinger(enriched["close"])
    bb_range = (bb_upper - bb_lower).replace(0.0, np.nan)
    enriched["stoch_k"], enriched["stoch_d"] = stochastic(enriched)
    enriched["adx"], enriched["plus_di"], enriched["minus_di"] = adx(enriched)
    enriched["bb_upper"] = bb_upper
    enriched["bb_middle"] = bb_middle
    enriched["bb_lower"] = bb_lower
    enriched["bb_bandwidth"] = (100.0 * bb_range / bb_middle.replace(0.0, np.nan)).fillna(0.0)
    enriched["bb_position"] = (
        (100.0 * (enriched["close"] - bb_lower) / bb_range).clip(0.0, 100.0).fillna(50.0)
    )
    enriched["mfi"] = mfi(enriched)
    enriched["obv"] = obv(enriched)
    enriched["obv_trend"] = obv_trend(enriched)
    enriched["relative_volume_20"] = relative_volume(enriched)
    return enriched


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return default if not np.isfinite(parsed) else parsed
