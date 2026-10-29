import numpy as np
import pandas as pd


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def _mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    typical = (df.high + df.low + df.close) / 3
    flow = typical * df.volume
    direction = typical.diff()
    positive = flow.where(direction > 0, 0).rolling(period).sum()
    negative = flow.where(direction < 0, 0).rolling(period).sum()
    ratio = positive / negative.replace(0, np.nan)
    return 100 - 100 / (1 + ratio)


def _stoch_rsi(rsi: pd.Series, period: int = 14, smooth_k: int = 3, smooth_d: int = 3):
    low = rsi.rolling(period).min()
    high = rsi.rolling(period).max()
    raw = 100 * (rsi - low) / (high - low).replace(0, np.nan)
    k = raw.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return k, d


def compute_indicators(candles: pd.DataFrame) -> pd.DataFrame:
    df = candles.copy()
    close = df["close"].astype(float)
    high, low = df["high"].astype(float), df["low"].astype(float)
    df["ema20"] = close.ewm(span=20, adjust=False).mean()
    df["ema50"] = close.ewm(span=50, adjust=False).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    df["rsi14"] = _rsi(close, 14)
    df["stoch_k"], df["stoch_d"] = _stoch_rsi(df["rsi14"], 14, 3, 3)
    df["mfi14"] = _mfi(df, 14)

    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    df["atr14"] = atr
    plus_di = 100 * plus_dm.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean() / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df["plus_di"], df["minus_di"] = plus_di, minus_di
    df["adx14"] = dx.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    return df


def analyze(candles: pd.DataFrame, symbol: str) -> dict:
    df = compute_indicators(candles).dropna()
    if len(df) < 2:
        raise ValueError("Not enough complete indicator values.")
    last, prev = df.iloc[-1], df.iloc[-2]
    score, reasons = 0, []
    tests = [
        (last.close > last.ema20, 12, "الإغلاق أعلى EMA20"),
        (last.ema20 > last.ema50, 12, "اتجاه EMA20 أعلى EMA50"),
        (last.macd_hist > 0, 12, "هيستوجرام MACD موجب"),
        (last.macd_hist > prev.macd_hist, 6, "زخم MACD يتحسن"),
        (last.plus_di > last.minus_di, 12, "+DI أعلى من -DI"),
        (last.adx14 >= 18, 8, "قوة الاتجاه مقبولة (ADX)"),
        (last.rsi14 >= 50 and last.rsi14 < 70, 10, "RSI في نطاق زخم إيجابي غير مفرط"),
        (last.mfi14 >= 50 and last.mfi14 < 80, 8, "MFI يدعم تدفق السيولة"),
        (last.stoch_k > last.stoch_d and prev.stoch_k <= prev.stoch_d and last.stoch_k < 40, 12, "تقاطع صاعد لـ Stoch RSI من نطاق منخفض"),
        (last.volume >= df.volume.tail(20).mean(), 8, "الحجم لا يقل عن متوسط 20 جلسة"),
    ]
    for passed, points, label in tests:
        if passed:
            score += points
            reasons.append(label)
    atr = float(last.atr14)
    close = float(last.close)
    entry_low, entry_high = close - 0.25 * atr, close + 0.10 * atr
    stop = close - 1.5 * atr
    target1, target2 = close + 2 * atr, close + 3 * atr
    signal = "WATCH" if score >= 50 else "AVOID"
    if score >= 75 and last.close > last.ema20 and last.plus_di > last.minus_di:
        signal = "CANDIDATE"
    timestamp = last.timestamp.isoformat() if hasattr(last.timestamp, "isoformat") else str(last.timestamp)
    return {
        "symbol": symbol, "as_of": timestamp, "close": round(close, 4),
        "score": int(score), "signal": signal, "reasons": reasons,
        "indicators": {key: (round(float(last[key]), 4) if pd.notna(last[key]) else None)
                       for key in ["ema20", "ema50", "macd", "macd_signal", "macd_hist",
                                   "stoch_k", "stoch_d", "mfi14", "rsi14", "plus_di", "minus_di", "adx14", "atr14"]},
        "plan": {"entry_zone": [round(entry_low, 4), round(entry_high, 4)],
                 "stop_loss": round(stop, 4), "target_1": round(target1, 4),
                 "target_2": round(target2, 4), "risk_reward_to_target_1": 2 / 1.5},
        "custom_indicator_33": {"status": "not_implemented", "note": "Exact formula required; no value is fabricated."},
        "disclaimer": "تحليل فني آلي لأغراض البحث، وليس ضمانًا للربح أو توصية شخصية."
    }
