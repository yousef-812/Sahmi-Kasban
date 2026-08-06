from __future__ import annotations

import numpy as np
import pandas as pd

from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.engines import MarketIndexEngine
from sahmi_kasban.index_resolver import EGX30_TICKERS, resolve_index_for_ticker
from sahmi_kasban.indicators import enrich_indicators, prepare_candles


def make_candles(direction: float = 0.15, rows: int = 240) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    trend = np.linspace(10.0, 10.0 * (1.0 + direction), rows)
    noise = rng.normal(0.0, 0.04, rows).cumsum() * 0.02
    close = np.maximum(1.0, trend + noise)
    open_price = close * (1 + rng.normal(0.0, 0.003, rows))
    high = np.maximum(open_price, close) * (1 + rng.uniform(0.002, 0.015, rows))
    low = np.minimum(open_price, close) * (1 - rng.uniform(0.002, 0.015, rows))
    volume = rng.integers(350_000, 1_600_000, rows)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=rows, freq="B", tz="UTC"),
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def make_index_candles(direction: float = 0.25, rows: int = 260) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    trend = np.linspace(10_000.0, 10_000.0 * (1.0 + direction), rows)
    noise = rng.normal(0.0, 0.004, rows).cumsum() * 0.01
    close = np.maximum(1000.0, trend + noise)
    open_price = close * (1 + rng.normal(0.0, 0.001, rows))
    high = np.maximum(open_price, close) * (1 + rng.uniform(0.001, 0.008, rows))
    low = np.minimum(open_price, close) * (1 - rng.uniform(0.001, 0.008, rows))
    volume = np.full(rows, 500_000)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=rows, freq="B", tz="UTC"),
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def make_breakout_stock(rows: int = 240) -> pd.DataFrame:
    close = np.linspace(10.0, 25.0, rows)
    close[-1] = 30.0
    high = close.copy()
    low = close * 0.995
    volume = np.full(rows, 1_000_000)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=rows, freq="B", tz="UTC"),
            "open": close.copy(),
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def test_market_index_engine_bullish_trend() -> None:
    engine = MarketIndexEngine(AnalysisConfig())
    result = engine.analyze(make_index_candles(0.25), {}, index_name="EGX30")
    assert result.name == "market_index"
    assert result.details["trend"] == "bullish"
    assert result.score >= 60
    assert result.details["index_name"] == "EGX30"


def test_market_index_engine_bearish_trend() -> None:
    engine = MarketIndexEngine(AnalysisConfig())
    result = engine.analyze(
        make_index_candles(-0.25),
        {},
        index_name="EGX70",
        stock_return_20d_pct=5.0,
    )
    assert result.details["trend"] == "bearish"
    assert result.score < 50
    assert "relative_strength_20d_pct" in result.details


def test_market_index_engine_relative_strength() -> None:
    engine = MarketIndexEngine(AnalysisConfig())
    result = engine.analyze(
        make_index_candles(0.10),
        {},
        index_name="EGX30",
        stock_return_20d_pct=12.5,
    )
    index_return = result.details["index_return_20d_pct"]
    expected_rs = round(12.5 - index_return, 2)
    assert result.details["relative_strength_20d_pct"] == expected_rs


def test_resolver_maps_egx30_members() -> None:
    assert "COMI" in EGX30_TICKERS
    assert resolve_index_for_ticker("COMI") == "EGX30"
    assert resolve_index_for_ticker(" comi ") == "EGX30"
    assert resolve_index_for_ticker("ZZZZ") == "EGX70"
    assert resolve_index_for_ticker("") == "EGX70"
    assert resolve_index_for_ticker("COMI", egx30_tickers={"HRHO"}) == "EGX70"


def test_no_index_skips_market_index_engine() -> None:
    report = SahmiKasbanAnalyzer(AnalysisConfig()).analyze("COMI", make_candles(0.30))
    assert "market_index" not in report.engines
    assert report.analysis_quality["engine_version"] == "core-v2.5"


def test_bearish_index_gates_buy_to_watch() -> None:
    analyzer = SahmiKasbanAnalyzer(AnalysisConfig())
    stock = make_breakout_stock()

    baseline = analyzer.analyze("COMI", stock)
    assert baseline.signal == "BUY"

    with_bull = analyzer.analyze(
        "COMI",
        stock,
        index=("EGX30", make_index_candles(0.25)),
    )
    assert with_bull.signal == "BUY"
    assert "market_index" in with_bull.engines
    assert with_bull.engines["market_index"].details["trend"] == "bullish"

    with_bear = analyzer.analyze(
        "COMI",
        stock,
        index=("EGX30", make_index_candles(-0.25)),
    )
    assert with_bear.signal == "WATCH"
    assert any(
        "market index trend is bearish" in warning for warning in with_bear.warnings
    )


def test_analyze_prepared_accepts_index() -> None:
    analyzer = SahmiKasbanAnalyzer(AnalysisConfig())
    prepared = enrich_indicators(prepare_candles(make_breakout_stock()))
    baseline = analyzer.analyze_prepared("COMI", prepared)
    assert baseline.signal == "BUY"
    report = analyzer.analyze_prepared(
        "COMI",
        prepared,
        index=("EGX70", make_index_candles(-0.25)),
    )
    assert "market_index" in report.engines
    assert report.signal == "WATCH"
