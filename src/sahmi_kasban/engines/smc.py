from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class SMCEngine(AnalysisEngine):
    name = "smc"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        recent = candles.tail(min(60, len(candles))).copy()
        latest = recent.iloc[-1]
        close = safe_float(latest["close"])

        previous_20 = recent.iloc[-21:-1] if len(recent) >= 21 else recent.iloc[:-1]
        previous_10 = recent.iloc[-11:-1] if len(recent) >= 11 else recent.iloc[:-1]
        high_20 = safe_float(previous_20["high"].max(), close)
        low_20 = safe_float(previous_20["low"].min(), close)
        high_10 = safe_float(previous_10["high"].max(), close)
        low_10 = safe_float(previous_10["low"].min(), close)

        bullish_bos = close > high_20 if not previous_20.empty else False
        bearish_bos = close < low_20 if not previous_20.empty else False

        prior_trend_up = False
        if len(recent) >= 25:
            earlier = recent.iloc[-25:-10]
            later = recent.iloc[-10:]
            prior_trend_up = later["close"].mean() > earlier["close"].mean()
        choch = (prior_trend_up and bearish_bos) or (not prior_trend_up and bullish_bos)

        latest_low = safe_float(latest["low"])
        latest_high = safe_float(latest["high"])
        liquidity_sweep_low = latest_low < low_10 and close > low_10
        liquidity_sweep_high = latest_high > high_10 and close < high_10

        fvg_bullish = False
        fvg_bearish = False
        if len(recent) >= 3:
            first = recent.iloc[-3]
            third = recent.iloc[-1]
            fvg_bullish = safe_float(third["low"]) > safe_float(first["high"])
            fvg_bearish = safe_float(third["high"]) < safe_float(first["low"])

        range_size = max(high_20 - low_20, 1e-9)
        range_position = (close - low_20) / range_size
        zone = (
            "discount"
            if range_position <= 0.45
            else "premium"
            if range_position >= 0.55
            else "equilibrium"
        )

        body = (recent["close"] - recent["open"]).abs()
        body_median = safe_float(body.tail(20).median())
        bullish_order_blocks: list[dict[str, float]] = []
        bearish_order_blocks: list[dict[str, float]] = []
        for index in range(max(1, len(recent) - 12), len(recent) - 1):
            candle = recent.iloc[index]
            next_candle = recent.iloc[index + 1]
            candle_body = abs(safe_float(candle["close"]) - safe_float(candle["open"]))
            displacement = abs(
                safe_float(next_candle["close"]) - safe_float(next_candle["open"])
            )
            if candle_body <= body_median and displacement >= body_median * 1.5:
                block = {
                    "low": round(safe_float(candle["low"]), 4),
                    "high": round(safe_float(candle["high"]), 4),
                }
                if (
                    safe_float(candle["close"]) < safe_float(candle["open"])
                    and safe_float(next_candle["close"]) > safe_float(next_candle["open"])
                ):
                    bullish_order_blocks.append(block)
                elif (
                    safe_float(candle["close"]) > safe_float(candle["open"])
                    and safe_float(next_candle["close"]) < safe_float(next_candle["open"])
                ):
                    bearish_order_blocks.append(block)

        score = 50.0
        reasons: list[str] = []
        if bullish_bos:
            score += 18
            reasons.append("Bullish break of structure")
        if bearish_bos:
            score -= 18
            reasons.append("Bearish break of structure")
        if liquidity_sweep_low:
            score += 12
            reasons.append("Sell-side liquidity sweep")
        if liquidity_sweep_high:
            score -= 10
            reasons.append("Buy-side liquidity sweep")
        if fvg_bullish:
            score += 7
            reasons.append("Bullish fair value gap")
        if fvg_bearish:
            score -= 7
            reasons.append("Bearish fair value gap")
        if zone == "discount":
            score += 8
            reasons.append("Price in discount zone")
        elif zone == "premium":
            score -= 5
        if bullish_order_blocks:
            score += min(8, len(bullish_order_blocks) * 3)
        if bearish_order_blocks:
            score -= min(8, len(bearish_order_blocks) * 3)

        score = self.clamp(score)
        context["smc_bias"] = (
            "bullish" if score >= 60 else "bearish" if score <= 40 else "neutral"
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(92.0, 55.0 + len(reasons) * 6),
            details={
                "bullish_bos": bullish_bos,
                "bearish_bos": bearish_bos,
                "choch": choch,
                "liquidity_sweep_low": liquidity_sweep_low,
                "liquidity_sweep_high": liquidity_sweep_high,
                "fvg_bullish": fvg_bullish,
                "fvg_bearish": fvg_bearish,
                "range_position": round(range_position, 3),
                "zone": zone,
                "bullish_order_blocks": bullish_order_blocks[-3:],
                "bearish_order_blocks": bearish_order_blocks[-3:],
            },
            reasons=reasons,
        )
