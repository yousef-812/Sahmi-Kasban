from __future__ import annotations

from statistics import pstdev

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class TechnicalEngine(AnalysisEngine):
    name = "technical"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        sma_20 = safe_float(latest.get("sma_20"), close)
        sma_50 = safe_float(latest.get("sma_50"), close)
        sma_200 = safe_float(latest.get("sma_200"), sma_50)
        rsi = safe_float(latest.get("rsi"), 50.0)
        macd = safe_float(latest.get("macd"))
        macd_signal = safe_float(latest.get("macd_signal"))
        macd_histogram = safe_float(latest.get("macd_histogram"))
        volume_ratio = safe_float(latest.get("volume_ratio"))
        return_5d = safe_float(latest.get("return_5d")) * 100.0
        return_20d = safe_float(latest.get("return_20d")) * 100.0
        slope_20 = safe_float(latest.get("trend_slope_20"))
        slope_60 = safe_float(latest.get("trend_slope_60"))
        trend_r2 = safe_float(latest.get("trend_r2_20"))
        adx_value = safe_float(latest.get("adx_14"))
        atr_pct = safe_float(latest.get("atr_pct"))
        bandwidth = safe_float(latest.get("bollinger_bandwidth")) * 100.0
        efficiency = safe_float(latest.get("price_efficiency_20"))

        reasons: list[str] = []
        trend_score = 50.0
        trend_score += 8.0 if close > sma_20 else -8.0
        trend_score += 10.0 if close > sma_50 else -10.0
        trend_score += 7.0 if sma_20 > sma_50 else -7.0
        if sma_200 > 0:
            trend_score += 7.0 if sma_50 > sma_200 else -7.0
        trend_score += max(-12.0, min(12.0, slope_20 * 32.0))
        trend_score += max(-8.0, min(8.0, slope_60 * 24.0))
        if adx_value >= 25:
            trend_score += 6.0 if slope_20 > 0 else -6.0 if slope_20 < 0 else 0.0
        trend_score = self.clamp(trend_score)

        momentum_score = 50.0
        if 48 <= rsi <= 66:
            momentum_score += 12.0
            reasons.append("RSI supports constructive momentum")
        elif 40 <= rsi < 48:
            momentum_score += 4.0
        elif rsi >= 78:
            momentum_score -= 15.0
            reasons.append("RSI is stretched")
        elif rsi <= 28:
            momentum_score -= 8.0
        macd_histogram_pct = macd_histogram / close * 100.0 if close > 0 else 0.0
        momentum_score += max(-12.0, min(12.0, macd_histogram_pct * 180.0))
        momentum_score += max(-8.0, min(8.0, return_5d * 0.8))
        momentum_score += max(-10.0, min(10.0, return_20d * 0.35))
        momentum_score = self.clamp(momentum_score)

        volume_score = 50.0
        if volume_ratio >= 1.5:
            if return_5d > 0:
                volume_score += 20.0
                reasons.append("Positive move confirmed by volume expansion")
            elif return_5d < 0:
                volume_score -= 20.0
                reasons.append("Selling pressure expanded with volume")
        elif volume_ratio >= 1.1:
            volume_score += 8.0 if return_5d >= 0 else -8.0
        elif 0 < volume_ratio < 0.65:
            volume_score -= 12.0
        volume_score = self.clamp(volume_score)

        stability_score = 65.0
        if atr_pct > self.config.atr_max_pct:
            stability_score -= 25.0
        elif atr_pct < self.config.atr_min_pct:
            stability_score -= 10.0
        if bandwidth > 18:
            stability_score -= 12.0
        if trend_r2 >= 0.65:
            stability_score += 12.0
        elif trend_r2 < 0.20:
            stability_score -= 8.0
        stability_score += (efficiency - 0.35) * 20.0
        stability_score = self.clamp(stability_score)

        components = {
            "trend": trend_score,
            "momentum": momentum_score,
            "volume_confirmation": volume_score,
            "stability": stability_score,
        }
        score = (
            trend_score * 0.45
            + momentum_score * 0.30
            + volume_score * 0.15
            + stability_score * 0.10
        )
        score = self.clamp(score)
        component_dispersion = pstdev(components.values())
        confidence = min(
            96.0,
            max(
                45.0,
                58.0
                + trend_r2 * 18.0
                + min(adx_value, 40.0) * 0.30
                - component_dispersion * 0.45,
            ),
        )
        trend = "uptrend" if trend_score >= 62 else "downtrend" if trend_score <= 38 else "sideways"
        context["technical_trend"] = trend
        context["technical_component_dispersion"] = component_dispersion
        if trend == "uptrend":
            reasons.append("Trend structure is positive")
        elif trend == "downtrend":
            reasons.append("Trend structure is negative")

        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "trend": trend,
                "close": round(close, 4),
                "sma_20": round(sma_20, 4),
                "sma_50": round(sma_50, 4),
                "sma_200": round(sma_200, 4),
                "rsi": round(rsi, 2),
                "macd": round(macd, 4),
                "macd_signal": round(macd_signal, 4),
                "macd_histogram_pct": round(macd_histogram_pct, 4),
                "volume_ratio": round(volume_ratio, 2),
                "return_5d_pct": round(return_5d, 2),
                "return_20d_pct": round(return_20d, 2),
                "trend_slope_20_pct_per_bar": round(slope_20, 4),
                "trend_slope_60_pct_per_bar": round(slope_60, 4),
                "trend_r2_20": round(trend_r2, 3),
                "adx_14": round(adx_value, 2),
                "atr_pct": round(atr_pct, 2),
                "bollinger_bandwidth_pct": round(bandwidth, 2),
                "price_efficiency_20": round(efficiency, 3),
                "component_scores": {key: round(value, 2) for key, value in components.items()},
                "component_dispersion": round(component_dispersion, 2),
            },
            reasons=reasons,
        )
