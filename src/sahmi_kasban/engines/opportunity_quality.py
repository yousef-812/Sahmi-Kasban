from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult

ELITE_MIN_DIRECTIONAL_SCORE = 80.0
ELITE_MIN_CONFIDENCE = 70.0
ELITE_MAX_RETURN_20D_PCT = 30.0
ELITE_MAX_ATR_PCT = 4.5
ELITE_MAX_TOTAL_RISK_PCT = 30.0
ELITE_MAX_ZERO_VOLUME_RATIO = 0.10


class OpportunityQualityEngine(AnalysisEngine):
    """Decide whether a strong BUY is robust enough for the elite tier.

    This engine is deliberately non-directional. It does not change the price
    forecast or the Core directional weights. It prevents a high momentum score
    alone from promoting an overextended or excessively volatile stock to the
    elite tier.
    """

    name = "opportunity_quality"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        return_20d_pct = safe_float(latest.get("return_20d")) * 100.0
        rsi = safe_float(latest.get("rsi"), 50.0)
        signal = str(context.get("signal", "WATCH")).upper()
        qualified = bool(context.get("qualified", False))
        final_score = safe_float(context.get("final_score"))
        confidence = safe_float(context.get("aggregate_confidence"))
        atr_pct = safe_float(context.get("atr_pct"))
        total_risk_pct = safe_float(context.get("total_risk_pct"))
        zero_volume_ratio = safe_float(context.get("zero_volume_ratio"))
        market_regime = str(context.get("market_regime", ""))
        timeframe_alignment = str(context.get("timeframe_alignment", ""))
        risk_level = str(context.get("risk_level", ""))
        bullish_count = int(safe_float(context.get("bullish_engine_count")))
        bearish_count = int(safe_float(context.get("bearish_engine_count")))
        directional_conflict = bool(context.get("directional_conflict", False))

        checks: dict[str, bool] = {
            "buy_signal": signal == "BUY",
            "qualified": qualified,
            "directional_score": final_score >= ELITE_MIN_DIRECTIONAL_SCORE,
            "aggregate_confidence": confidence >= ELITE_MIN_CONFIDENCE,
            "directional_consensus": (
                bullish_count >= 4 and bearish_count == 0 and not directional_conflict
            ),
            "bullish_market_regime": market_regime == "bullish",
            "bullish_timeframe_alignment": timeframe_alignment == "bullish",
            "momentum_not_overextended": return_20d_pct <= ELITE_MAX_RETURN_20D_PCT,
            "atr_controlled": 0 < atr_pct <= ELITE_MAX_ATR_PCT,
            "risk_controlled": (
                risk_level != "high" and total_risk_pct <= ELITE_MAX_TOTAL_RISK_PCT
            ),
            "trading_continuity": zero_volume_ratio <= ELITE_MAX_ZERO_VOLUME_RATIO,
        }
        weights: Mapping[str, float] = {
            "buy_signal": 8.0,
            "qualified": 8.0,
            "directional_score": 14.0,
            "aggregate_confidence": 10.0,
            "directional_consensus": 12.0,
            "bullish_market_regime": 8.0,
            "bullish_timeframe_alignment": 8.0,
            "momentum_not_overextended": 14.0,
            "atr_controlled": 10.0,
            "risk_controlled": 6.0,
            "trading_continuity": 2.0,
        }
        readiness_score = sum(weights[name] for name, passed in checks.items() if passed)
        failed_checks = [name for name, passed in checks.items() if not passed]
        engine_ready = not failed_checks

        return EngineResult(
            name=self.name,
            score=readiness_score,
            confidence=90.0 if engine_ready else 75.0,
            status="complete" if engine_ready else "rejected",
            details={
                "model_version": "elite-quality-v2.2",
                "engine_ready": engine_ready,
                "readiness_score": round(readiness_score, 2),
                "checks": checks,
                "failed_checks": failed_checks,
                "thresholds": {
                    "min_directional_score": ELITE_MIN_DIRECTIONAL_SCORE,
                    "min_confidence": ELITE_MIN_CONFIDENCE,
                    "max_return_20d_pct": ELITE_MAX_RETURN_20D_PCT,
                    "max_atr_pct": ELITE_MAX_ATR_PCT,
                    "max_total_risk_pct": ELITE_MAX_TOTAL_RISK_PCT,
                    "max_zero_volume_ratio": ELITE_MAX_ZERO_VOLUME_RATIO,
                },
                "metrics": {
                    "final_score": round(final_score, 2),
                    "aggregate_confidence": round(confidence, 2),
                    "return_20d_pct": round(return_20d_pct, 2),
                    "rsi": round(rsi, 2),
                    "atr_pct": round(atr_pct, 2),
                    "total_risk_pct": round(total_risk_pct, 2),
                    "zero_volume_ratio": round(zero_volume_ratio, 3),
                    "market_regime": market_regime,
                    "timeframe_alignment": timeframe_alignment,
                    "risk_level": risk_level,
                    "bullish_engine_count": bullish_count,
                    "bearish_engine_count": bearish_count,
                },
            },
            reasons=(
                ["Elite quality gates passed"]
                if engine_ready
                else [f"Elite gate failed: {name}" for name in failed_checks]
            ),
        )
