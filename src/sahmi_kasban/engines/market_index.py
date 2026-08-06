from __future__ import annotations

import numpy as np
import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class MarketIndexEngine(AnalysisEngine):
    """Context engine reporting the direction of a market index.

    The engine is advisory only: it is never blended into the directional
    score and never reweights ``DEFAULT_WEIGHTS``. Its trend feeds a
    BUY->WATCH gate in the orchestrator when the index is bearish.
    """

    name = "market_index"

    def analyze(
        self,
        candles: pd.DataFrame,
        context: dict[str, object],
        *,
        index_name: str = "",
        stock_return_20d_pct: float | None = None,
    ) -> EngineResult:
        frame = candles.reset_index(drop=True).copy()
        close = pd.to_numeric(frame["close"], errors="coerce")
        volume = pd.to_numeric(frame["volume"], errors="coerce").fillna(0.0)

        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        sma_200 = close.rolling(200).mean()
        returns = close.pct_change()
        annualized_vol = returns.rolling(20).std() * (252**0.5)
        avg_volume_20 = volume.rolling(20).mean()
        return_20d = close.pct_change(20)

        last_close = safe_float(close.iloc[-1], 0.0)
        last_sma20 = safe_float(sma_20.iloc[-1], last_close)
        last_sma50 = safe_float(sma_50.iloc[-1], last_close)
        last_sma200 = safe_float(sma_200.iloc[-1], last_sma50)
        last_vol = safe_float(annualized_vol.iloc[-1], 0.0) * 100.0
        last_volume = safe_float(volume.iloc[-1], 0.0)
        last_avg_volume = safe_float(avg_volume_20.iloc[-1], last_volume)
        index_return_20d = safe_float(return_20d.iloc[-1], 0.0) * 100.0

        bull = sum(
            [
                last_close > last_sma20,
                last_close > last_sma50,
                last_sma20 > last_sma50,
                last_sma50 > last_sma200,
            ]
        )
        bear = sum(
            [
                last_close < last_sma20,
                last_close < last_sma50,
                last_sma20 < last_sma50,
                last_sma50 < last_sma200,
            ]
        )

        if bull >= 3:
            trend = "bullish"
            score = 72.0 + bull * 5.0
        elif bear >= 3:
            trend = "bearish"
            score = 28.0 - bear * 3.0
        else:
            trend = "sideways"
            score = 50.0

        if last_vol > 65.0:
            score -= 8.0
        elif last_vol < 35.0:
            score += 4.0
        volume_ratio = last_volume / last_avg_volume if last_avg_volume > 0 else 0.0
        if last_avg_volume > 0 and last_volume > last_avg_volume * 1.25:
            score += 4.0 if trend == "bullish" else -2.0 if trend == "bearish" else 1.0

        score = self.clamp(score)

        rs_20d = None
        if stock_return_20d_pct is not None and np.isfinite(float(stock_return_20d_pct)):
            rs_20d = round(float(stock_return_20d_pct) - index_return_20d, 2)

        context["market_index_trend"] = trend
        context["market_index_score"] = score

        details: dict[str, object] = {
            "model_version": "market-index-v2.5",
            "index_name": index_name,
            "trend": trend,
            "index_close": round(last_close, 2),
            "index_return_20d_pct": round(index_return_20d, 2),
            "annualized_volatility_pct": round(last_vol, 2),
            "bullish_checks": bull,
            "bearish_checks": bear,
            "volume_ratio": round(volume_ratio, 2),
        }
        if rs_20d is not None:
            details["relative_strength_20d_pct"] = rs_20d

        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(95.0, 55.0 + abs(score - 50.0)),
            details=details,
            reasons=[f"Market index trend: {trend} ({index_name})"],
        )
