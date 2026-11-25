from __future__ import annotations

import pandas as pd

from sahmi_kasban.indicators import (
    adx,
    bollinger,
    breakdown_flag,
    breakout_flag,
    enrich_indicators,
    high_52w,
    low_52w,
    mfi,
    obv,
    obv_trend,
    performance_pct,
    relative_volume,
    stochastic,
)

NEW_SCANNER_COLUMNS = (
    "stoch_k",
    "stoch_d",
    "adx",
    "plus_di",
    "minus_di",
    "bb_upper",
    "bb_middle",
    "bb_lower",
    "bb_bandwidth",
    "bb_position",
    "mfi",
    "obv",
    "obv_trend",
    "relative_volume_20",
)

LEGACY_COLUMNS = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "sma_20",
    "sma_50",
    "sma_200",
    "macd",
    "macd_signal",
    "rsi",
    "atr",
    "avg_volume_20",
    "vwap_20",
    "return_1d",
    "return_20d",
    "volatility_20d",
)


def _trend_frame(rows: int = 300, start: float = 100.0, step: float = 1.0) -> pd.DataFrame:
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


def _flat_frame(rows: int = 60, price: float = 50.0) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [price] * rows,
            "high": [price + 1.0] * rows,
            "low": [price - 1.0] * rows,
            "close": [price] * rows,
            "volume": [1000.0] * rows,
        }
    )


def test_enrich_indicators_adds_scanner_columns() -> None:
    enriched = enrich_indicators(_trend_frame())

    for column in LEGACY_COLUMNS + NEW_SCANNER_COLUMNS:
        assert column in enriched.columns, column


def test_enrich_indicators_scanner_columns_are_finite_after_warmup() -> None:
    enriched = enrich_indicators(_trend_frame())

    finite = (
        "stoch_k",
        "stoch_d",
        "adx",
        "plus_di",
        "minus_di",
        "bb_bandwidth",
        "bb_position",
        "mfi",
        "obv",
        "obv_trend",
        "relative_volume_20",
    )
    for column in finite:
        assert not enriched[column].iloc[60:].isna().any(), column

    for column in ("bb_upper", "bb_middle", "bb_lower"):
        assert not enriched[column].iloc[60:].isna().any(), column


def test_stochastic_marks_overbought_in_uptrend() -> None:
    frame = _trend_frame()
    fast_k, slow_d = stochastic(frame)

    assert fast_k.iloc[-1] > 50.0
    assert 0.0 <= fast_k.iloc[-1] <= 100.0
    assert 0.0 <= slow_d.iloc[-1] <= 100.0
    assert not fast_k.isna().any()
    assert not slow_d.isna().any()


def test_stochastic_on_flat_market_is_neutral() -> None:
    fast_k, slow_d = stochastic(_flat_frame())

    assert fast_k.iloc[-1] == 50.0
    assert slow_d.iloc[-1] == 50.0


def test_adx_confirms_directional_trend() -> None:
    adx_value, plus_di, minus_di = adx(_trend_frame())

    assert adx_value.iloc[-1] > 10.0
    assert plus_di.iloc[-1] > minus_di.iloc[-1]
    assert not adx_value.isna().any()
    assert not plus_di.isna().any()
    assert not minus_di.isna().any()


def test_adx_on_flat_market_has_no_direction() -> None:
    adx_value, plus_di, minus_di = adx(_flat_frame())

    assert plus_di.iloc[-1] == 0.0
    assert minus_di.iloc[-1] == 0.0
    assert adx_value.iloc[-1] == 0.0


def test_bollinger_bands_are_ordered() -> None:
    upper, middle, lower = bollinger(_trend_frame()["close"])

    assert (upper.iloc[60:] > middle.iloc[60:]).all()
    assert (middle.iloc[60:] > lower.iloc[60:]).all()
    assert not upper.iloc[60:].isna().any()


def test_mfi_saturates_on_one_sided_flow() -> None:
    assert mfi(_trend_frame()).iloc[-1] > 99.0
    assert mfi(_trend_frame(step=-1.0, start=200.0)).iloc[-1] < 1.0


def test_obv_accumulates_on_uptrend() -> None:
    frame = _trend_frame()

    assert obv(frame).iloc[-1] > 0.0
    assert obv_trend(frame, window=20) == 1
    assert obv_trend(_trend_frame(step=-1.0, start=200.0), window=20) == -1
    assert obv_trend(_flat_frame()) == 0


def test_relative_volume_reports_neutral_for_constant_volume() -> None:
    frame = _trend_frame()
    enriched = enrich_indicators(frame)

    assert abs(relative_volume(frame).iloc[-1] - 1.0) < 1e-9
    assert abs(enriched["relative_volume_20"].iloc[-1] - 1.0) < 1e-9


def test_performance_pct_matches_expected_change() -> None:
    frame = _trend_frame()
    performance = performance_pct(frame["close"], 20)

    expected = ((frame["close"].iloc[-1] / frame["close"].iloc[-1 - 20]) - 1.0) * 100.0
    assert abs(performance.iloc[-1] - expected) < 1e-9
    assert performance.iloc[-1] > 0.0


def test_52_week_extremes_are_windowed() -> None:
    frame = _trend_frame()

    assert high_52w(frame["close"]) == 399.0
    assert low_52w(frame["close"]) == 148.0
    assert high_52w(frame["close"], window=1000) == 399.0
    assert low_52w(frame["close"], window=1000) == 100.0


def test_breakout_and_breakdown_flags() -> None:
    assert breakout_flag(_trend_frame()["close"]).iloc[-1] == 1.0
    assert breakdown_flag(_trend_frame()["close"]).iloc[-1] == 0.0
    assert breakout_flag(_trend_frame(step=-1.0, start=200.0)["close"]).iloc[-1] == 0.0
    assert breakdown_flag(_trend_frame(step=-1.0, start=200.0)["close"]).iloc[-1] == 1.0


def test_breakout_flag_is_zero_before_enough_history() -> None:
    frame = _trend_frame(rows=15)

    assert breakout_flag(frame["close"]).iloc[0] == 0.0
    assert breakdown_flag(frame["close"]).iloc[0] == 0.0
