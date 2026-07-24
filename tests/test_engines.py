from __future__ import annotations

import numpy as np
import pandas as pd

from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer


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


def test_full_analysis_returns_all_core_engines() -> None:
    analyzer = SahmiKasbanAnalyzer(AnalysisConfig())
    report = analyzer.analyze("COMI", make_candles())

    assert report.ticker == "COMI"
    assert report.qualified is True
    assert report.trade_plan is not None
    assert 0 <= report.final_score <= 100
    assert {
        "stock_qualification",
        "market_environment",
        "technical",
        "smc",
        "multi_timeframe",
        "quantitative",
        "risk",
        "scenario",
    }.issubset(report.engines)


def test_illiquid_stock_is_rejected() -> None:
    candles = make_candles()
    candles["volume"] = 100
    analyzer = SahmiKasbanAnalyzer(AnalysisConfig(min_average_volume=100_000))
    report = analyzer.analyze("TEST", candles)

    assert report.qualified is False
    assert report.signal == "AVOID"


def test_position_value_respects_configured_cap() -> None:
    config = AnalysisConfig(capital=100_000, max_position_value=12_000, risk_per_trade=0.01)
    report = SahmiKasbanAnalyzer(config).analyze("SWDY", make_candles())

    assert report.trade_plan is not None
    assert report.trade_plan.position_value <= config.max_position_value + 1
    assert report.trade_plan.risk_amount <= config.capital * config.risk_per_trade + 1
