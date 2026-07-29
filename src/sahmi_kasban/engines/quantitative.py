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
        momentum_5 = safe_float(candles["close"].pct_change(5).iloc[-1])
        momentum_20 = safe_float(candles["close"].pct_change(20).iloc[-1])
        momentum_60 = safe_float(candles["close"].pct_change(60).iloc[-1])
        volatility = safe_float(returns.tail(20).std())
        downside = returns.tail(60)[returns.tail(60) < 0]
        downside_volatility = safe_float(downside.std(), volatility)

        volume_window = candles["volume"].tail(60)
        volume_std = safe_float(volume_window.std())
        volume_z = (
            (safe_float(last["volume"]) - safe_float(volume_window.mean())) / volume_std
            if volume_std > 0
            else 0.0
        )

        trend_factor = momentum_5 * 2.0 + momentum_20 * 3.0 + momentum_60 * 1.5
        risk_penalty = volatility * 4.0 + downside_volatility * 2.0
        volume_factor = max(-2.0, min(2.0, volume_z)) * 0.08
        raw_edge = trend_factor - risk_penalty + volume_factor

        # Replay evidence showed that multiplying this edge by six forced too many
        # observations to 0% or 100%. Momentum is already represented in raw_edge,
        # so an additional score bump would count the same evidence twice.
        bullish_probability = self._logistic(raw_edge)
        score = bullish_probability * 100.0

        sample_quality = min(1.0, len(returns) / 252.0)
        edge_strength = min(1.0, abs(bullish_probability - 0.5) * 2.0)
        confidence = min(90.0, 50.0 + sample_quality * 25.0 + edge_strength * 15.0)

        context["bullish_probability"] = bullish_probability
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "model_version": "momentum-logit-v3-calibrated",
                "sample_size": len(returns),
                "sample_quality_pct": round(sample_quality * 100, 2),
                "momentum_5d_pct": round(momentum_5 * 100, 2),
                "momentum_20d_pct": round(momentum_20 * 100, 2),
                "momentum_60d_pct": round(momentum_60 * 100, 2),
                "volatility_20d_pct": round(volatility * 100, 2),
                "downside_volatility_pct": round(downside_volatility * 100, 2),
                "volume_z_score": round(volume_z, 2),
                "raw_edge": round(raw_edge, 6),
                "bullish_probability_pct": round(bullish_probability * 100, 2),
            },
            reasons=[f"Model bullish probability: {bullish_probability * 100:.1f}%"],
        )
