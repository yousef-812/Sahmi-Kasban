from __future__ import annotations

import math

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class QuantitativeEngine(AnalysisEngine):
    name = "quantitative"

    @staticmethod
    def _logistic(value: float) -> float:
        value = max(-20.0, min(20.0, value))
        return 1.0 / (1.0 + math.exp(-value))

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        returns = candles["close"].pct_change().dropna()
        last = candles.iloc[-1]
        momentum_5 = safe_float(last.get("return_5d"))
        momentum_20 = safe_float(last.get("return_20d"))
        momentum_60 = safe_float(last.get("return_60d"))
        volatility_20 = safe_float(last.get("volatility_20d"))
        volatility_60 = safe_float(last.get("volatility_60d"), volatility_20)
        downside = returns.tail(60)[returns.tail(60) < 0]
        downside_volatility = safe_float(downside.std(), volatility_20)
        drawdown_60 = safe_float(last.get("drawdown_60d"))
        trend_r2 = safe_float(last.get("trend_r2_60"))
        efficiency = safe_float(last.get("price_efficiency_20"))

        volume_window = candles["volume"].tail(60)
        volume_std = safe_float(volume_window.std())
        volume_z = (
            (safe_float(last["volume"]) - safe_float(volume_window.mean())) / volume_std
            if volume_std > 0
            else 0.0
        )
        positive_ratio_20 = float((returns.tail(20) > 0).mean()) if len(returns) >= 5 else 0.5
        positive_ratio_60 = float((returns.tail(60) > 0).mean()) if len(returns) >= 20 else positive_ratio_20
        autocorrelation = safe_float(returns.tail(60).autocorr(lag=1)) if len(returns) >= 20 else 0.0

        blended_momentum = momentum_5 * 0.20 + momentum_20 * 0.45 + momentum_60 * 0.35
        horizon_risk = max(volatility_20 * math.sqrt(20.0), 0.01)
        risk_adjusted_momentum = max(-3.0, min(3.0, blended_momentum / horizon_risk))
        persistence = positive_ratio_20 * 0.65 + positive_ratio_60 * 0.35
        downside_ratio = downside_volatility / volatility_20 if volatility_20 > 0 else 1.0
        volatility_regime_penalty = (
            max(0.0, volatility_20 / volatility_60 - 1.25) if volatility_60 > 0 else 0.0
        )
        drawdown_penalty = max(0.0, min(1.5, abs(min(drawdown_60, 0.0)) * 4.0))

        raw_edge = (
            risk_adjusted_momentum * 0.95
            + (persistence - 0.50) * 2.6
            + (trend_r2 - 0.45) * 0.85
            + (efficiency - 0.35) * 0.65
            + max(-2.0, min(2.0, volume_z)) * 0.08
            + max(-0.5, min(0.5, autocorrelation)) * 0.25
            - max(0.0, downside_ratio - 1.0) * 0.35
            - volatility_regime_penalty * 0.45
            - drawdown_penalty * 0.40
        )
        bullish_probability = self._logistic(raw_edge * 1.35)
        score = self.clamp(bullish_probability * 100.0)

        sample_confidence = min(1.0, len(returns) / 180.0)
        stability = max(0.0, min(1.0, trend_r2 * 0.55 + efficiency * 0.45))
        confidence = min(
            92.0,
            48.0 + sample_confidence * 24.0 + stability * 18.0,
        )
        context["bullish_probability"] = bullish_probability
        context["quantitative_edge"] = raw_edge
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "momentum_5d_pct": round(momentum_5 * 100.0, 2),
                "momentum_20d_pct": round(momentum_20 * 100.0, 2),
                "momentum_60d_pct": round(momentum_60 * 100.0, 2),
                "risk_adjusted_momentum": round(risk_adjusted_momentum, 3),
                "positive_day_ratio_20": round(positive_ratio_20, 3),
                "positive_day_ratio_60": round(positive_ratio_60, 3),
                "volatility_20d_pct": round(volatility_20 * 100.0, 2),
                "volatility_60d_pct": round(volatility_60 * 100.0, 2),
                "downside_volatility_pct": round(downside_volatility * 100.0, 2),
                "downside_volatility_ratio": round(downside_ratio, 3),
                "drawdown_60d_pct": round(drawdown_60 * 100.0, 2),
                "trend_r2_60": round(trend_r2, 3),
                "price_efficiency_20": round(efficiency, 3),
                "return_autocorrelation_1": round(autocorrelation, 3),
                "volume_z_score": round(volume_z, 2),
                "raw_edge": round(raw_edge, 4),
                "bullish_probability_pct": round(bullish_probability * 100.0, 2),
                "probability_type": "heuristic_calibratable_edge",
            },
            reasons=[
                f"Heuristic bullish edge probability: {bullish_probability * 100.0:.1f}%",
                "Probability requires historical calibration before being treated as predictive",
            ],
        )
