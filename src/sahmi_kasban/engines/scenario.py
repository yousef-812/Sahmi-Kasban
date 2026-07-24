from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult, TradePlan


class ScenarioEngine(AnalysisEngine):
    name = "scenario"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"), close * 0.02)
        technical_score = safe_float(context.get("technical_score"), 50.0)
        smc_score = safe_float(context.get("smc_score"), 50.0)
        quantitative_score = safe_float(context.get("quantitative_score"), 50.0)
        combined = technical_score * 0.4 + smc_score * 0.3 + quantitative_score * 0.3

        bullish_probability = self.clamp(combined)
        bearish_probability = self.clamp(100.0 - combined)
        base_probability = max(10.0, 100.0 - abs(combined - 50.0) * 1.6)
        total = bullish_probability + bearish_probability + base_probability
        bullish_probability = bullish_probability / total * 100.0
        bearish_probability = bearish_probability / total * 100.0
        base_probability = base_probability / total * 100.0

        plan = context.get("trade_plan")
        if isinstance(plan, TradePlan):
            bullish_target = plan.target_2
            base_target = plan.target_1
            bearish_target = plan.stop_loss
        else:
            bullish_target = close + atr_value * 3.5
            base_target = close + atr_value * 2.0
            bearish_target = max(0.01, close - atr_value * 2.0)

        score = self.clamp(bullish_probability + base_probability * 0.5)
        return EngineResult(
            name=self.name,
            score=score,
            confidence=75.0,
            details={
                "bullish": {
                    "probability_pct": round(bullish_probability, 2),
                    "target": round(bullish_target, 4),
                },
                "base": {
                    "probability_pct": round(base_probability, 2),
                    "target": round(base_target, 4),
                },
                "bearish": {
                    "probability_pct": round(bearish_probability, 2),
                    "target": round(bearish_target, 4),
                },
            },
            reasons=["Scenario probabilities are model estimates, not guarantees"],
        )
