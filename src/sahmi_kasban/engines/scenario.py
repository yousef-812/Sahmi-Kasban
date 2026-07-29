from __future__ import annotations

import math
from statistics import pstdev

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult, TradePlan


class ScenarioEngine(AnalysisEngine):
    name = "scenario"

    @staticmethod
    def _logistic(value: float) -> float:
        value = max(-20.0, min(20.0, value))
        return 1.0 / (1.0 + math.exp(-value))

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"), close * 0.02)
        component_scores = [
            safe_float(context.get("technical_score"), 50.0),
            safe_float(context.get("smc_score"), 50.0),
            safe_float(context.get("multi_timeframe_score"), 50.0),
            safe_float(context.get("quantitative_score"), 50.0),
            safe_float(context.get("risk_score"), 50.0),
        ]
        combined = (
            component_scores[0] * 0.28
            + component_scores[1] * 0.18
            + component_scores[2] * 0.20
            + component_scores[3] * 0.22
            + component_scores[4] * 0.12
        )
        dispersion = pstdev(component_scores)
        directional_probability = self._logistic((combined - 50.0) / 11.0)
        neutrality = 1.0 - min(1.0, abs(combined - 50.0) / 35.0)
        uncertainty = min(0.62, 0.12 + dispersion / 90.0 + neutrality * 0.18)
        directional_mass = 1.0 - uncertainty
        bullish_probability = directional_mass * directional_probability
        bearish_probability = directional_mass * (1.0 - directional_probability)
        base_probability = uncertainty

        plan = context.get("trade_plan")
        if isinstance(plan, TradePlan):
            bullish_target = plan.target_2
            base_target = plan.target_1
            bearish_target = plan.stop_loss
        else:
            bullish_target = close + atr_value * 3.5
            base_target = close + atr_value * 2.0
            bearish_target = max(0.01, close - atr_value * 2.0)

        score = self.clamp(
            bullish_probability * 100.0 + base_probability * 50.0
        )
        confidence = max(35.0, min(88.0, (1.0 - uncertainty) * 100.0))
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "bullish": {
                    "probability_pct": round(bullish_probability * 100.0, 2),
                    "target": round(bullish_target, 4),
                },
                "base": {
                    "probability_pct": round(base_probability * 100.0, 2),
                    "target": round(base_target, 4),
                },
                "bearish": {
                    "probability_pct": round(bearish_probability * 100.0, 2),
                    "target": round(bearish_target, 4),
                },
                "component_mean": round(combined, 2),
                "component_dispersion": round(dispersion, 2),
                "uncertainty_pct": round(uncertainty * 100.0, 2),
                "calibration_status": "requires_walk_forward_validation",
            },
            reasons=[
                "Scenario probabilities incorporate engine disagreement",
                "Probabilities are model estimates and must be validated historically",
            ],
        )
