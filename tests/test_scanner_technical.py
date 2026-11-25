from __future__ import annotations

import pandas as pd

from sahmi_kasban.scanner import (
    SCANNER_VERSION,
    build_technical_snapshot,
    technical_rating,
    technical_score,
)

EXPECTED_KEYS = {
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
}


def _frame(rows: int = 300, start: float = 100.0, step: float = 1.0) -> pd.DataFrame:
    closes = [start + step * index for index in range(rows)]
    return pd.DataFrame(
        {
            "open": closes,
            "high": [price + 1.0 for price in closes],
            "low": [price - 1.0 for price in closes],
            "close": closes,
            "volume": [1000.0] * rows,
        }
    )


def _flat_then_jump(rows: int = 60, price: float = 100.0, jump: float = 10.0) -> pd.DataFrame:
    closes = [price] * rows + [price + jump]
    return pd.DataFrame(
        {
            "open": closes,
            "high": [value + 1.0 for value in closes],
            "low": [value - 1.0 for value in closes],
            "close": closes,
            "volume": [1000.0] * (rows + 1),
        }
    )


def test_snapshot_contains_exact_contract_keys() -> None:
    snapshot = build_technical_snapshot(_frame(), symbol="TEST")

    assert set(snapshot) == EXPECTED_KEYS
    assert snapshot["symbol"] == "TEST"
    assert snapshot["timeframe"] == "1D"
    assert snapshot["candlesUsed"] == 300
    assert SCANNER_VERSION == "scanner-tech-v1"


def test_uptrend_scores_buy() -> None:
    snapshot = build_technical_snapshot(_frame(), symbol="UP")

    assert snapshot["technicalScore"] > 40.0
    assert snapshot["technicalRating"] == "buy"
    assert snapshot["breakout20"] == 1
    assert snapshot["breakdown20"] == 0
    assert snapshot["obvTrend"] == 1
    assert snapshot["performance20d"] > 0.0


def test_downtrend_scores_sell() -> None:
    snapshot = build_technical_snapshot(_frame(step=-1.0, start=399.0), symbol="DOWN")

    assert snapshot["technicalScore"] < -40.0
    assert snapshot["technicalRating"] == "sell"
    assert snapshot["breakout20"] == 0
    assert snapshot["breakdown20"] == 1
    assert snapshot["obvTrend"] == -1
    assert snapshot["performance20d"] < 0.0


def test_flat_market_is_neutral() -> None:
    snapshot = build_technical_snapshot(_frame(step=0.0), symbol="FLAT")

    assert -40.0 < snapshot["technicalScore"] < 40.0
    assert snapshot["technicalRating"] == "neutral"


def test_ema_and_macd_cross_up_on_bullish_jump() -> None:
    snapshot = build_technical_snapshot(_flat_then_jump(jump=10.0), symbol="JUMP_UP")

    assert snapshot["emaCrossUp"] == 1
    assert snapshot["emaCrossDown"] == 0
    assert snapshot["ema20Above50"] == 1
    assert snapshot["macdCrossUp"] == 1
    assert snapshot["macdCrossDown"] == 0
    assert snapshot["macdBullish"] == 1


def test_ema_and_macd_cross_down_on_bearish_jump() -> None:
    snapshot = build_technical_snapshot(_flat_then_jump(jump=-10.0), symbol="JUMP_DOWN")

    assert snapshot["emaCrossDown"] == 1
    assert snapshot["emaCrossUp"] == 0
    assert snapshot["ema20Above50"] == 0
    assert snapshot["macdCrossDown"] == 1
    assert snapshot["macdCrossUp"] == 0
    assert snapshot["macdBullish"] == 0


def test_symbol_and_timeframe_passthrough() -> None:
    snapshot = build_technical_snapshot(_frame(rows=60), timeframe="60M", symbol=None)

    assert snapshot["symbol"] is None
    assert snapshot["timeframe"] == "60M"


def test_score_is_bounded_to_contract_range() -> None:
    bullish = build_technical_snapshot(_frame(), symbol="UP")
    bearish = build_technical_snapshot(_frame(step=-1.0, start=399.0), symbol="DOWN")

    for snapshot in (bullish, bearish):
        score = technical_score(snapshot)
        assert -100.0 <= score <= 100.0


def test_rating_thresholds() -> None:
    assert technical_rating(40.0) == "buy"
    assert technical_rating(100.0) == "buy"
    assert technical_rating(-40.0) == "sell"
    assert technical_rating(-100.0) == "sell"
    assert technical_rating(39.99) == "neutral"
    assert technical_rating(-39.99) == "neutral"
    assert technical_rating(0.0) == "neutral"
