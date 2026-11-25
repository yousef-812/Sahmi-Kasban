from __future__ import annotations

import pandas as pd

from sahmi_kasban.indicators import (
    breakdown_flag,
    breakout_flag,
    ema,
    enrich_indicators,
    high_52w,
    low_52w,
    obv_trend,
    performance_pct,
    prepare_candles,
    safe_float,
)

SCANNER_VERSION = "scanner-tech-v1"

TECHNICAL_WEIGHTS: dict[str, float] = {
    "ma_trend": 0.20,
    "rsi": 0.12,
    "macd": 0.18,
    "adx": 0.10,
    "bollinger": 0.08,
    "stochastic": 0.08,
    "mfi": 0.06,
    "volume": 0.08,
    "breakout": 0.06,
    "performance": 0.10,
}

SNAPSHOT_KEYS = (
    "symbol",
    "timeframe",
    "candleTimestamp",
    "candlesUsed",
    "technicalScore",
    "technicalRating",
    "rsi14",
    "macd",
    "macdSignal",
    "macdHistogram",
    "macdBullish",
    "macdCrossUp",
    "macdCrossDown",
    "adx14",
    "plusDi14",
    "minusDi14",
    "atr14",
    "atrPercent",
    "bbUpper",
    "bbMiddle",
    "bbLower",
    "bbPosition",
    "bbBandwidth",
    "sma20",
    "sma50",
    "sma200",
    "ema20",
    "ema50",
    "priceVsSma20",
    "priceVsSma50",
    "priceVsSma200",
    "ema20Above50",
    "emaCrossUp",
    "emaCrossDown",
    "relativeVolume20",
    "stochasticK",
    "stochasticD",
    "mfi14",
    "obvTrend",
    "breakout20",
    "breakdown20",
    "performance5d",
    "performance20d",
    "performance60d",
    "high52Week",
    "low52Week",
)


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _percent_vs(value: float, reference: float) -> float:
    if reference <= 0:
        return 0.0
    return (value / reference - 1.0) * 100.0


def _last(series: pd.Series) -> float:
    return safe_float(series.iloc[-1])


def _cross_up(
    previous_left: float, previous_right: float, current_left: float, current_right: float
) -> int:
    return int(previous_left <= previous_right and current_left > current_right)


def _cross_down(
    previous_left: float, previous_right: float, current_left: float, current_right: float
) -> int:
    return int(previous_left >= previous_right and current_left < current_right)


def build_technical_snapshot(
    df: pd.DataFrame,
    *,
    timeframe: str = "1D",
    symbol: str | None = None,
) -> dict[str, object]:
    prepared = prepare_candles(df)
    enriched = enrich_indicators(prepared)
    latest = enriched.iloc[-1]
    previous = enriched.iloc[-2] if len(enriched) >= 2 else latest

    close = safe_float(latest["close"])
    ema_20_series = ema(enriched["close"], 20)
    ema_50_series = ema(enriched["close"], 50)
    ema_20 = safe_float(ema_20_series.iloc[-1])
    ema_50 = safe_float(ema_50_series.iloc[-1])
    if len(enriched) >= 2:
        previous_ema_20 = safe_float(ema_20_series.iloc[-2])
        previous_ema_50 = safe_float(ema_50_series.iloc[-2])
    else:
        previous_ema_20 = ema_20
        previous_ema_50 = ema_50

    atr14 = safe_float(latest.get("atr"))
    macd = safe_float(latest.get("macd"))
    macd_signal = safe_float(latest.get("macd_signal"))
    previous_macd = safe_float(previous.get("macd"))
    previous_macd_signal = safe_float(previous.get("macd_signal"))
    sma_20 = safe_float(latest.get("sma_20"))
    sma_50 = safe_float(latest.get("sma_50"))
    sma_200 = safe_float(latest.get("sma_200"))

    candle_timestamp = None
    if "timestamp" in enriched.columns:
        raw_timestamp = enriched["timestamp"].iloc[-1]
        if pd.notna(raw_timestamp):
            candle_timestamp = pd.Timestamp(raw_timestamp).isoformat()

    snapshot: dict[str, object] = {
        "symbol": symbol,
        "timeframe": timeframe,
        "candleTimestamp": candle_timestamp,
        "candlesUsed": int(len(enriched)),
        "rsi14": _last(enriched["rsi"]),
        "macd": macd,
        "macdSignal": macd_signal,
        "macdHistogram": macd - macd_signal,
        "macdBullish": int(macd > macd_signal),
        "macdCrossUp": _cross_up(previous_macd, previous_macd_signal, macd, macd_signal),
        "macdCrossDown": _cross_down(previous_macd, previous_macd_signal, macd, macd_signal),
        "adx14": _last(enriched["adx"]),
        "plusDi14": _last(enriched["plus_di"]),
        "minusDi14": _last(enriched["minus_di"]),
        "atr14": atr14,
        "atrPercent": _percent_vs(atr14, close),
        "bbUpper": _last(enriched["bb_upper"]),
        "bbMiddle": _last(enriched["bb_middle"]),
        "bbLower": _last(enriched["bb_lower"]),
        "bbPosition": _last(enriched["bb_position"]),
        "bbBandwidth": _last(enriched["bb_bandwidth"]),
        "sma20": sma_20,
        "sma50": sma_50,
        "sma200": sma_200,
        "ema20": ema_20,
        "ema50": ema_50,
        "priceVsSma20": _percent_vs(close, sma_20),
        "priceVsSma50": _percent_vs(close, sma_50),
        "priceVsSma200": _percent_vs(close, sma_200),
        "ema20Above50": int(ema_20 > ema_50),
        "emaCrossUp": _cross_up(previous_ema_20, previous_ema_50, ema_20, ema_50),
        "emaCrossDown": _cross_down(previous_ema_20, previous_ema_50, ema_20, ema_50),
        "relativeVolume20": _last(enriched["relative_volume_20"]),
        "stochasticK": _last(enriched["stoch_k"]),
        "stochasticD": _last(enriched["stoch_d"]),
        "mfi14": _last(enriched["mfi"]),
        "obvTrend": int(obv_trend(prepared)),
        "breakout20": int(safe_float(breakout_flag(enriched["close"]).iloc[-1])),
        "breakdown20": int(safe_float(breakdown_flag(enriched["close"]).iloc[-1])),
        "performance5d": _last(performance_pct(enriched["close"], 5)),
        "performance20d": _last(performance_pct(enriched["close"], 20)),
        "performance60d": _last(performance_pct(enriched["close"], 60)),
        "high52Week": high_52w(enriched["close"]),
        "low52Week": low_52w(enriched["close"]),
    }
    score = technical_score(snapshot)
    snapshot["technicalScore"] = score
    snapshot["technicalRating"] = technical_rating(score)
    return snapshot


def _component_ma_trend(snapshot: dict[str, object]) -> float:
    readings = [
        safe_float(snapshot.get("priceVsSma20")),
        safe_float(snapshot.get("priceVsSma50")),
        safe_float(snapshot.get("priceVsSma200")),
    ]
    signals = [value / abs(value) if value > 0 else (-1.0 if value < 0 else 0.0) for value in readings]
    signals.append(1.0 if safe_float(snapshot.get("ema20Above50")) > 0 else -1.0)
    return sum(signals) / len(signals)


def _component_rsi(snapshot: dict[str, object]) -> float:
    rsi14 = safe_float(snapshot.get("rsi14"), 50.0)
    if rsi14 >= 75.0:
        return -0.6
    if rsi14 >= 50.0:
        return (rsi14 - 50.0) / 25.0
    if rsi14 >= 30.0:
        return (rsi14 - 50.0) / 20.0
    return -0.8


def _component_macd(snapshot: dict[str, object]) -> float:
    atr14 = abs(safe_float(snapshot.get("atr14")))
    histogram = safe_float(snapshot.get("macdHistogram"))
    if atr14 > 0:
        value = _clamp(histogram / atr14 * 3.0)
    else:
        value = 1.0 if safe_float(snapshot.get("macdBullish")) > 0 else -1.0
    if safe_float(snapshot.get("macdCrossUp")) > 0:
        value += 0.25
    if safe_float(snapshot.get("macdCrossDown")) > 0:
        value -= 0.25
    return _clamp(value)


def _component_adx(snapshot: dict[str, object]) -> float:
    adx14 = safe_float(snapshot.get("adx14"))
    plus_di = safe_float(snapshot.get("plusDi14"))
    minus_di = safe_float(snapshot.get("minusDi14"))
    total = plus_di + minus_di
    if total <= 1e-9:
        return 0.0
    strength = min(1.0, adx14 / 25.0)
    return _clamp((plus_di - minus_di) / total) * strength


def _component_bollinger(snapshot: dict[str, object]) -> float:
    return _clamp((safe_float(snapshot.get("bbPosition"), 50.0) - 50.0) / 50.0)


def _component_stochastic(snapshot: dict[str, object]) -> float:
    fast = _clamp((safe_float(snapshot.get("stochasticK"), 50.0) - 50.0) / 50.0)
    slow = _clamp((safe_float(snapshot.get("stochasticD"), 50.0) - 50.0) / 50.0)
    return fast * 0.7 + slow * 0.3


def _component_mfi(snapshot: dict[str, object]) -> float:
    return _clamp((safe_float(snapshot.get("mfi14"), 50.0) - 50.0) / 50.0)


def _component_volume(snapshot: dict[str, object]) -> float:
    relative = safe_float(snapshot.get("relativeVolume20"), 1.0)
    if safe_float(snapshot.get("priceVsSma20")) > 0:
        direction = 1.0
    elif safe_float(snapshot.get("priceVsSma20")) < 0:
        direction = -1.0
    else:
        direction = 0.0
    return _clamp(relative - 1.0) * direction


def _component_breakout(snapshot: dict[str, object]) -> float:
    if safe_float(snapshot.get("breakout20")) > 0:
        return 1.0
    if safe_float(snapshot.get("breakdown20")) > 0:
        return -1.0
    return 0.0


def _component_performance(snapshot: dict[str, object]) -> float:
    readings = [
        safe_float(snapshot.get("performance5d"), float("nan")),
        safe_float(snapshot.get("performance20d"), float("nan")),
        safe_float(snapshot.get("performance60d"), float("nan")),
    ]
    valid = [value for value in readings if value == value]
    if not valid:
        return 0.0
    clipped = [_clamp(value / 10.0) for value in valid]
    return sum(clipped) / len(clipped)


def technical_score(snapshot: dict[str, object]) -> float:
    components = {
        "ma_trend": _component_ma_trend(snapshot),
        "rsi": _component_rsi(snapshot),
        "macd": _component_macd(snapshot),
        "adx": _component_adx(snapshot),
        "bollinger": _component_bollinger(snapshot),
        "stochastic": _component_stochastic(snapshot),
        "mfi": _component_mfi(snapshot),
        "volume": _component_volume(snapshot),
        "breakout": _component_breakout(snapshot),
        "performance": _component_performance(snapshot),
    }
    total = sum(TECHNICAL_WEIGHTS[key] * value for key, value in components.items())
    return round(_clamp(100.0 * total, -100.0, 100.0), 2)


def technical_rating(score: float) -> str:
    if score >= 40.0:
        return "buy"
    if score <= -40.0:
        return "sell"
    return "neutral"
