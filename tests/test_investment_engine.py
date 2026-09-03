from __future__ import annotations

import pandas as pd

from sahmi_kasban import AnalysisConfig
from sahmi_kasban.engines.investment import FundamentalInvestmentEngine


def test_calculate_metrics_growth_stock():
    metrics = FundamentalInvestmentEngine.calculate_metrics(
        ticker="FWRY",
        current_price=20.0,
        pe_ratio=14.0,
        pb_ratio=2.5,
        dividend_yield_pct=1.5,
        roe_pct=22.0,
        total_debt=100_000_000,
        market_cap=2_000_000_000,
        eps=1.8,
        sma_200=18.0,
    )
    assert metrics.ticker == "FWRY"
    assert metrics.investment_category == "growth"
    assert metrics.investment_score >= 70.0
    assert metrics.fair_value is not None
    assert metrics.margin_of_safety_pct is not None
    assert len(metrics.strengths) > 0


def test_calculate_metrics_dividend_stock():
    metrics = FundamentalInvestmentEngine.calculate_metrics(
        ticker="ABUK",
        current_price=50.0,
        pe_ratio=6.5,
        dividend_yield_pct=11.2,
        roe_pct=28.0,
        eps=8.0,
        sma_200=45.0,
    )
    assert metrics.investment_category == "dividend"
    assert metrics.investment_score >= 80.0
    assert any("توزيعات" in s for s in metrics.strengths)


def test_calculate_metrics_value_stock():
    metrics = FundamentalInvestmentEngine.calculate_metrics(
        ticker="SWDY",
        current_price=30.0,
        pe_ratio=5.2,
        dividend_yield_pct=4.5,
        roe_pct=12.0,
        eps=5.5,
        sma_200=28.0,
    )
    assert metrics.investment_category == "value"
    assert metrics.margin_of_safety_pct is not None and metrics.margin_of_safety_pct > 25.0


def test_engine_analyze():
    engine = FundamentalInvestmentEngine(AnalysisConfig())
    candles = pd.DataFrame([
        {"open": 10.0, "high": 10.5, "low": 9.8, "close": 10.2, "volume": 1000, "sma_200": 9.5}
    ])
    context = {
        "ticker": "ETEL",
        "pe_ratio": 7.0,
        "dividend_yield_pct": 8.0,
        "roe_pct": 18.0,
        "eps": 1.5,
    }
    result = engine.analyze(candles, context)
    assert result.name == "investment"
    assert result.score > 70.0
    assert "investment_metrics" in context
    assert context["investment_metrics"]["ticker"] == "ETEL"
