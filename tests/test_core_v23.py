from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.market import MarketEnvironmentEngine
from sahmi_kasban.engines.opportunity_quality import OpportunityQualityEngine
from sahmi_kasban.engines.risk import RiskEngine
from sahmi_kasban.indicators import enrich_indicators
from sahmi_kasban.models import AnalysisConfig


def _candles(*, growth: float = 0.004, breakout: bool = False) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for index in range(260):
        close = 100.0 * ((1.0 + growth) ** index)
        rows.append(
            {
                "open": close * 0.995,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "volume": 1_000_000.0,
            }
        )
    if breakout:
        prior_high = max(row["high"] for row in rows[-21:-1])
        close = prior_high * 1.03
        rows[-1] = {
            "open": close * 0.98,
            "high": close * 1.01,
            "low": close * 0.97,
            "close": close,
            "volume": 2_200_000.0,
        }
    return enrich_indicators(pd.DataFrame(rows))


def _context(**overrides: object) -> dict[str, object]:
    context: dict[str, object] = {
        "signal": "BUY",
        "qualified": True,
        "final_score": 84.0,
        "aggregate_confidence": 78.0,
        "bullish_engine_count": 5,
        "bearish_engine_count": 0,
        "directional_conflict": False,
        "market_regime": "bullish",
        "market_regime_profile": "trend_bullish",
        "timeframe_alignment": "bullish",
        "atr_pct": 4.0,
        "total_risk_pct": 24.0,
        "risk_level": "low",
        "zero_volume_ratio": 0.0,
        "average_turnover_egp": 10_000_000.0,
    }
    context.update(overrides)
    return context


def test_balanced_elite_uses_adaptive_liquidity_limits() -> None:
    result = OpportunityQualityEngine(AnalysisConfig()).analyze(
        _candles(),
        _context(atr_pct=5.0, total_risk_pct=31.0, risk_level="medium"),
    )

    assert result.details["model_version"] == "elite-quality-v2.3-regime-aware"
    assert result.details["selected_profile"] == "balanced"
    assert result.details["balanced_ready"] is True
    assert result.details["aggressive_ready"] is False
    assert result.details["adaptive_limits"]["balanced_max_atr_pct"] == 5.25
    assert result.details["recommended_position_multiplier"] == 1.0


def test_aggressive_elite_requires_breakout_volume_and_smaller_position() -> None:
    candles = _candles(growth=0.003, breakout=True)
    candles.loc[candles.index[-1], "rsi"] = 72.0
    candles.loc[candles.index[-1], "return_20d"] = 0.18
    candles.loc[candles.index[-1], "avg_volume_20"] = 1_000_000.0

    result = OpportunityQualityEngine(AnalysisConfig()).analyze(
        candles,
        _context(
            atr_pct=6.5,
            total_risk_pct=38.0,
            risk_level="medium",
            market_regime_profile="breakout_bullish",
        ),
    )

    assert result.details["balanced_ready"] is False
    assert result.details["aggressive_ready"] is True
    assert result.details["selected_profile"] == "aggressive"
    assert result.details["recommended_position_multiplier"] == 0.5
    assert result.details["aggressive_checks"]["breakout_confirmed"] is True
    assert result.details["aggressive_checks"]["volume_confirmation"] is True


def test_aggressive_elite_rejects_unconfirmed_high_atr_move() -> None:
    candles = _candles(growth=0.003, breakout=False)
    candles.loc[candles.index[-1], "rsi"] = 72.0
    candles.loc[candles.index[-1], "return_20d"] = 0.18

    result = OpportunityQualityEngine(AnalysisConfig()).analyze(
        candles,
        _context(atr_pct=6.5, total_risk_pct=38.0, risk_level="medium"),
    )

    assert result.details["engine_ready"] is False
    assert "breakout_confirmed" in result.details["aggressive_failed_checks"]
    assert "volume_confirmation" in result.details["aggressive_failed_checks"]


def test_market_environment_publishes_regime_profile() -> None:
    result = MarketEnvironmentEngine(AnalysisConfig()).analyze(
        _candles(growth=0.004, breakout=True),
        {},
    )

    assert result.details["model_version"] == "market-regime-v2.3"
    assert result.details["regime"] == "bullish"
    assert result.details["regime_profile"] == "breakout_bullish"


def test_trade_plan_uses_realistic_five_session_targets() -> None:
    result = RiskEngine(AnalysisConfig()).analyze(_candles(), {})
    plan = result.details["trade_plan"]

    assert result.details["model_version"] == "risk-plan-v2.3-atr-5-session"
    assert result.details["horizon_sessions"] == 5
    assert plan["reward_risk_1"] == 1.0
    assert plan["reward_risk_2"] == 1.75
