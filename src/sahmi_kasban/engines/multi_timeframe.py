from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class MultiTimeframeEngine(AnalysisEngine):
    name = "multi_timeframe"

    @staticmethod
    def _trend_score(close: pd.Series) -> tuple[str, float]:
        if len(close) < 8:
            return "insufficient", 50.0
        fast_window = min(5, max(2, len(close) // 4))
        slow_window = min(20, max(fast_window + 1, len(close) // 2))
        fast = safe_float(close.tail(fast_window).mean())
        slow = safe_float(close.tail(slow_window).mean())
        last = safe_float(close.iloc[-1])
        if last > fast > slow:
            return "bullish", 75.0
        if last < fast < slow:
            return "bearish", 25.0
        if last > slow:
            return "weak_bullish", 60.0
        if last < slow:
            return "weak_bearish", 40.0
        return "sideways", 50.0

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        daily_trend, daily_score = self._trend_score(candles["close"])

        if "timestamp" in candles.columns and candles["timestamp"].notna().all():
            indexed = candles.set_index("timestamp")
            weekly_close = indexed["close"].resample("W-FRI").last().dropna()
            monthly_close = indexed["close"].resample("ME").last().dropna()
        else:
            weekly_close = candles["close"].groupby(candles.index // 5).last()
            monthly_close = candles["close"].groupby(candles.index // 21).last()

        weekly_trend, weekly_score = self._trend_score(weekly_close)
        monthly_trend, monthly_score = self._trend_score(monthly_close)
        score = daily_score * 0.45 + weekly_score * 0.35 + monthly_score * 0.20

        bullish = sum(
            "bullish" in trend for trend in (daily_trend, weekly_trend, monthly_trend)
        )
        bearish = sum(
            "bearish" in trend for trend in (daily_trend, weekly_trend, monthly_trend)
        )
        aligned = bullish == 3 or bearish == 3
        if aligned:
            score += 5 if bullish == 3 else -5

        score = self.clamp(score)
        context["timeframe_alignment"] = (
            "bullish" if bullish >= 2 else "bearish" if bearish >= 2 else "mixed"
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=88.0 if aligned else 68.0,
            details={
                "daily": {"trend": daily_trend, "score": daily_score},
                "weekly": {"trend": weekly_trend, "score": weekly_score},
                "monthly": {"trend": monthly_trend, "score": monthly_score},
                "aligned": aligned,
                "alignment": context["timeframe_alignment"],
            },
            reasons=[f"Timeframe alignment: {context['timeframe_alignment']}"],
        )
