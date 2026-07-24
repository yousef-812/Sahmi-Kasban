from __future__ import annotations

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
        volume = safe_float(latest.get("volume"))
        avg_volume = safe_float(latest.get("avg_volume_20"), volume)
        return_20d = safe_float(latest.get("return_20d")) * 100

        score = 50.0
        reasons: list[str] = []

        if close > sma_20:
            score += 7
            reasons.append("Price above SMA20")
        else:
            score -= 7
        if close > sma_50:
            score += 9
            reasons.append("Price above SMA50")
        else:
            score -= 9
        if sma_20 > sma_50:
            score += 8
            reasons.append("SMA20 above SMA50")
        else:
            score -= 5
        if sma_50 > sma_200 and sma_200 > 0:
            score += 9
            reasons.append("Long-term trend positive")
        elif sma_200 > 0:
            score -= 8

        if 45 <= rsi <= 65:
            score += 10
            reasons.append("RSI in constructive range")
        elif 30 <= rsi < 45:
            score += 4
        elif rsi > 75:
            score -= 12
            reasons.append("RSI overbought")
        elif rsi < 25:
            score -= 5

        if macd > macd_signal:
            score += 10
            reasons.append("MACD bullish")
        else:
            score -= 7

        volume_ratio = volume / avg_volume if avg_volume > 0 else 0
        if volume_ratio >= 1.5:
            score += 8 if return_20d >= 0 else -5
            reasons.append("Volume expansion")
        if return_20d > 8:
            score += 6
        elif return_20d < -8:
            score -= 8

        score = self.clamp(score)
        trend = "uptrend" if score >= 65 else "downtrend" if score <= 40 else "sideways"
        context["technical_trend"] = trend
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(96.0, 60.0 + abs(score - 50.0) * 0.7),
            details={
                "trend": trend,
                "close": round(close, 4),
                "sma_20": round(sma_20, 4),
                "sma_50": round(sma_50, 4),
                "sma_200": round(sma_200, 4),
                "rsi": round(rsi, 2),
                "macd": round(macd, 4),
                "macd_signal": round(macd_signal, 4),
                "volume_ratio": round(volume_ratio, 2),
                "return_20d_pct": round(return_20d, 2),
            },
            reasons=reasons,
        )
