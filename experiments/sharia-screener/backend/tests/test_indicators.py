import pandas as pd
import numpy as np
from app.indicators import compute_indicators, analyze


def sample_candles(n=180):
    close = np.linspace(10, 18, n) + np.sin(np.arange(n) / 5) * 0.2
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="B", tz="UTC"),
        "open": close - 0.05,
        "high": close + 0.2,
        "low": close - 0.2,
        "close": close,
        "volume": np.full(n, 100_000.0),
    })


def test_indicators_have_expected_columns():
    result = compute_indicators(sample_candles())
    for name in ["rsi14", "macd_hist", "stoch_k", "mfi14", "plus_di", "minus_di", "adx14", "atr14"]:
        assert name in result.columns


def test_analysis_is_explainable_and_does_not_fabricate_custom_indicator():
    result = analyze(sample_candles(), "TEST")
    assert 0 <= result["score"] <= 100
    assert result["signal"] in {"CANDIDATE", "WATCH", "AVOID"}
    assert "reasons" in result
    assert result["custom_indicator_33"]["status"] == "not_implemented"
