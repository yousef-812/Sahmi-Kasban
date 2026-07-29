from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class SMCEngine(AnalysisEngine):
    name = "smc"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        recent = candles.tail(min(80, len(candles))).copy()
        latest = recent.iloc[-1]
        close = safe_float(latest["close"])
        open_price = safe_float(latest["open"])
        atr_value = max(safe_float(latest.get("atr")), close * 0.005)
        volume_ratio = safe_float(latest.get("volume_ratio"))

        previous_20 = recent.iloc[-21:-1] if len(recent) >= 21 else recent.iloc[:-1]
        previous_10 = recent.iloc[-11:-1] if len(recent) >= 11 else recent.iloc[:-1]
        high_20 = safe_float(previous_20["high"].max(), close)
        low_20 = safe_float(previous_20["low"].min(), close)
        high_10 = safe_float(previous_10["high"].max(), close)
        low_10 = safe_float(previous_10["low"].min(), close)

        candle_bodies = (recent["close"] - recent["open"]).abs()
        body_median = max(safe_float(candle_bodies.tail(20).median()), close * 0.001)
        latest_body = abs(close - open_price)
        displacement_ratio = latest_body / body_median
        raw_bullish_break = close > high_20 if not previous_20.empty else False
        raw_bearish_break = close < low_20 if not previous_20.empty else False
        bullish_bos = (
            raw_bullish_break
            and close > open_price
            and displacement_ratio >= 1.20
            and volume_ratio >= 0.90
        )
        bearish_bos = (
            raw_bearish_break
            and close < open_price
            and displacement_ratio >= 1.20
            and volume_ratio >= 0.90
        )

        prior_trend_up = False
        if len(recent) >= 30:
            earlier = recent.iloc[-30:-12]
            later = recent.iloc[-12:-1]
            prior_trend_up = later["close"].mean() > earlier["close"].mean()
        choch = (prior_trend_up and bearish_bos) or (not prior_trend_up and bullish_bos)

        latest_low = safe_float(latest["low"])
        latest_high = safe_float(latest["high"])
        lower_wick = min(open_price, close) - latest_low
        upper_wick = latest_high - max(open_price, close)
        liquidity_sweep_low = (
            latest_low < low_10
            and close > low_10
            and lower_wick >= latest_body * 0.60
        )
        liquidity_sweep_high = (
            latest_high > high_10
            and close < high_10
            and upper_wick >= latest_body * 0.60
        )

        fvg_bullish = False
        fvg_bearish = False
        fvg_size_atr = 0.0
        if len(recent) >= 3:
            first = recent.iloc[-3]
            third = recent.iloc[-1]
            bullish_gap = safe_float(third["low"]) - safe_float(first["high"])
            bearish_gap = safe_float(first["low"]) - safe_float(third["high"])
            if bullish_gap > atr_value * 0.12:
                fvg_bullish = True
                fvg_size_atr = bullish_gap / atr_value
            elif bearish_gap > atr_value * 0.12:
                fvg_bearish = True
                fvg_size_atr = bearish_gap / atr_value

        range_size = max(high_20 - low_20, 1e-9)
        range_position = (close - low_20) / range_size
        zone = (
            "discount"
            if range_position <= 0.42
            else "premium"
            if range_position >= 0.58
            else "equilibrium"
        )

        bullish_order_blocks: list[dict[str, float]] = []
        bearish_order_blocks: list[dict[str, float]] = []
        for index in range(max(1, len(recent) - 16), len(recent) - 1):
            candle = recent.iloc[index]
            next_candle = recent.iloc[index + 1]
            candle_body = abs(safe_float(candle["close"]) - safe_float(candle["open"]))
            next_body = abs(
                safe_float(next_candle["close"]) - safe_float(next_candle["open"])
            )
            if candle_body <= body_median and next_body >= body_median * 1.65:
                block = {
                    "low": round(safe_float(candle["low"]), 4),
                    "high": round(safe_float(candle["high"]), 4),
                }
                bullish_confirmation = (
                    safe_float(candle["close"]) < safe_float(candle["open"])
                    and safe_float(next_candle["close"]) > safe_float(candle["high"])
                )
                bearish_confirmation = (
                    safe_float(candle["close"]) > safe_float(candle["open"])
                    and safe_float(next_candle["close"]) < safe_float(candle["low"])
                )
                if bullish_confirmation:
                    bullish_order_blocks.append(block)
                elif bearish_confirmation:
                    bearish_order_blocks.append(block)

        score = 50.0
        reasons: list[str] = []
        if bullish_bos:
            score += 20.0
            reasons.append("Confirmed bullish break of structure")
        elif raw_bullish_break:
            score += 5.0
            reasons.append("Bullish break lacks displacement or volume confirmation")
        if bearish_bos:
            score -= 20.0
            reasons.append("Confirmed bearish break of structure")
        elif raw_bearish_break:
            score -= 5.0
            reasons.append("Bearish break lacks displacement or volume confirmation")
        if liquidity_sweep_low:
            score += 11.0
            reasons.append("Sell-side liquidity sweep with rejection")
        if liquidity_sweep_high:
            score -= 11.0
            reasons.append("Buy-side liquidity sweep with rejection")
        if fvg_bullish:
            score += min(8.0, 4.0 + fvg_size_atr * 2.0)
            reasons.append("Bullish fair value gap above minimum ATR size")
        if fvg_bearish:
            score -= min(8.0, 4.0 + fvg_size_atr * 2.0)
            reasons.append("Bearish fair value gap above minimum ATR size")
        if zone == "discount" and not bearish_bos:
            score += 6.0
        elif zone == "premium" and not bullish_bos:
            score -= 5.0
        if bullish_order_blocks:
            score += min(7.0, len(bullish_order_blocks) * 2.5)
        if bearish_order_blocks:
            score -= min(7.0, len(bearish_order_blocks) * 2.5)

        score = self.clamp(score)
        evidence_count = sum(
            (
                bullish_bos,
                bearish_bos,
                liquidity_sweep_low,
                liquidity_sweep_high,
                fvg_bullish,
                fvg_bearish,
                bool(bullish_order_blocks),
                bool(bearish_order_blocks),
            )
        )
        confidence = min(
            92.0,
            48.0 + evidence_count * 6.0 + min(displacement_ratio, 3.0) * 4.0,
        )
        context["smc_bias"] = (
            "bullish" if score >= 60 else "bearish" if score <= 40 else "neutral"
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "bullish_bos": bullish_bos,
                "bearish_bos": bearish_bos,
                "raw_bullish_break": raw_bullish_break,
                "raw_bearish_break": raw_bearish_break,
                "choch": choch,
                "liquidity_sweep_low": liquidity_sweep_low,
                "liquidity_sweep_high": liquidity_sweep_high,
                "fvg_bullish": fvg_bullish,
                "fvg_bearish": fvg_bearish,
                "fvg_size_atr": round(fvg_size_atr, 3),
                "displacement_ratio": round(displacement_ratio, 3),
                "volume_ratio": round(volume_ratio, 2),
                "range_position": round(range_position, 3),
                "zone": zone,
                "bullish_order_blocks": bullish_order_blocks[-3:],
                "bearish_order_blocks": bearish_order_blocks[-3:],
                "evidence_count": evidence_count,
            },
            reasons=reasons,
        )
