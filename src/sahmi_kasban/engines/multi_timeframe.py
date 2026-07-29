from __future__ import annotations

import math

import numpy as np
import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.models import EngineResult


class MultiTimeframeEngine(AnalysisEngine):
    name = "multi_timeframe"

    @staticmethod
    def _trend_metrics(close: pd.Series) -> dict[str, object]:
        cleaned = close.dropna().astype(float)
        sample = cleaned.tail(min(40, len(cleaned)))
        if len(sample) < 8 or (sample <= 0).any():
            return {
                "trend": "insufficient",
                "score": 50.0,
                "reliability": 0.0,
                "slope_pct_per_bar": 0.0,
                "r_squared": 0.0,
                "observations": len(sample),
            }

        x = np.arange(len(sample), dtype=float)
        y = np.log(sample.to_numpy())
        coefficients = np.polyfit(x, y, 1)
        predicted = np.polyval(coefficients, x)
        residual = float(np.square(y - predicted).sum())
        total = float(np.square(y - y.mean()).sum())
        r_squared = 0.0 if total <= 0 else max(0.0, min(1.0, 1.0 - residual / total))
        slope_pct = float(np.expm1(coefficients[0]) * 100.0)
        score = 50.0 + math.tanh(slope_pct * 2.5) * 35.0
        score = max(0.0, min(100.0, score))
        reliability = min(1.0, len(sample) / 24.0) * (0.30 + 0.70 * r_squared)
        trend = (
            "bullish"
            if score >= 62
            else "bearish"
            if score <= 38
            else "weak_bullish"
            if score >= 54
            else "weak_bearish"
            if score <= 46
            else "sideways"
        )
        return {
            "trend": trend,
            "score": round(score, 2),
            "reliability": round(reliability, 3),
            "slope_pct_per_bar": round(slope_pct, 4),
            "r_squared": round(r_squared, 3),
            "observations": len(sample),
        }

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        daily = self._trend_metrics(candles["close"])

        if "timestamp" in candles.columns and candles["timestamp"].notna().all():
            indexed = candles.set_index("timestamp")
            weekly_close = indexed["close"].resample("W-FRI").last().dropna()
            monthly_close = indexed["close"].resample("ME").last().dropna()
        else:
            weekly_close = candles["close"].groupby(candles.index // 5).last()
            monthly_close = candles["close"].groupby(candles.index // 21).last()

        weekly = self._trend_metrics(weekly_close)
        monthly = self._trend_metrics(monthly_close)
        frames = {"daily": daily, "weekly": weekly, "monthly": monthly}
        base_weights = {"daily": 0.45, "weekly": 0.35, "monthly": 0.20}
        effective_weights = {
            name: base_weights[name] * float(frame["reliability"])
            for name, frame in frames.items()
        }
        used_weight = sum(effective_weights.values())
        if used_weight <= 0:
            score = 50.0
        else:
            score = sum(
                float(frames[name]["score"]) * weight
                for name, weight in effective_weights.items()
            ) / used_weight

        reliable_trends = [
            str(frame["trend"])
            for frame in frames.values()
            if float(frame["reliability"]) >= 0.35
        ]
        bullish = sum("bullish" in trend for trend in reliable_trends)
        bearish = sum("bearish" in trend for trend in reliable_trends)
        aligned = len(reliable_trends) >= 2 and (bullish == len(reliable_trends) or bearish == len(reliable_trends))
        if aligned:
            score += 5.0 if bullish == len(reliable_trends) else -5.0
        score = self.clamp(score)

        alignment = "bullish" if bullish >= 2 else "bearish" if bearish >= 2 else "mixed"
        average_reliability = (
            sum(float(frame["reliability"]) for frame in frames.values()) / len(frames)
        )
        confidence = min(
            94.0,
            45.0 + average_reliability * 40.0 + (9.0 if aligned else 0.0),
        )
        context["timeframe_alignment"] = alignment
        context["timeframe_reliability"] = average_reliability
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                **frames,
                "aligned": aligned,
                "alignment": alignment,
                "reliable_timeframes": len(reliable_trends),
                "effective_weights": {
                    name: round(weight / used_weight, 3) if used_weight > 0 else 0.0
                    for name, weight in effective_weights.items()
                },
            },
            reasons=[
                f"Timeframe alignment: {alignment}",
                f"Reliable timeframes: {len(reliable_trends)} of 3",
            ],
        )
