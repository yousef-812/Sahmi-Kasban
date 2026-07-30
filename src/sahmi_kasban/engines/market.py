from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class MarketEnvironmentEngine(AnalysisEngine):
    name = "market_environment"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        sma_20 = safe_float(latest.get("sma_20"), close)
        sma_50 = safe_float(latest.get("sma_50"), close)
        sma_200 = safe_float(latest.get("sma_200"), sma_50)
        volatility = safe_float(latest.get("volatility_20d")) * (252**0.5) * 100
        atr_value = safe_float(latest.get("atr"))
        atr_pct = atr_value / close * 100.0 if close > 0 else 0.0
        volume = safe_float(latest.get("volume"))
        avg_volume = safe_float(latest.get("avg_volume_20"), volume)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 0.0
        return_20d_pct = safe_float(latest.get("return_20d")) * 100.0
        return_5d_pct = 0.0
        if len(candles) >= 6:
            close_5d = safe_float(candles.iloc[-6].get("close"))
            if close_5d > 0:
                return_5d_pct = (close / close_5d - 1.0) * 100.0

        bullish_points = sum(
            [
                close > sma_20,
                close > sma_50,
                sma_20 > sma_50,
                sma_50 > sma_200,
            ]
        )
        bearish_points = sum(
            [
                close < sma_20,
                close < sma_50,
                sma_20 < sma_50,
                sma_50 < sma_200,
            ]
        )

        if bullish_points >= 3:
            regime = "bullish"
            score = 72 + bullish_points * 5
        elif bearish_points >= 3:
            regime = "bearish"
            score = 28 - bearish_points * 3
        else:
            regime = "sideways"
            score = 50

        if regime == "bullish" and volume_ratio >= 1.5 and return_5d_pct > 2:
            profile = "breakout_bullish"
        elif regime == "bullish" and volatility > 65:
            profile = "speculative_bullish"
        elif regime == "bullish":
            profile = "trend_bullish"
        elif regime == "bearish" and volatility > 65:
            profile = "risk_off_volatile"
        elif regime == "bearish":
            profile = "trend_bearish"
        elif abs(return_20d_pct) <= 8 and volatility <= 55:
            profile = "sideways_rotation"
        else:
            profile = "mixed_volatile"

        if volatility > 65:
            score -= 8
        elif volatility < 35:
            score += 4
        if avg_volume > 0 and volume > avg_volume * 1.25:
            score += 4 if regime == "bullish" else -2 if regime == "bearish" else 1

        score = self.clamp(score)
        context["market_regime"] = regime
        context["market_regime_profile"] = profile
        context["annualized_volatility"] = volatility
        context["market_volume_ratio"] = volume_ratio
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(95.0, 55.0 + abs(score - 50.0)),
            details={
                "model_version": "market-regime-v2.3",
                "regime": regime,
                "regime_profile": profile,
                "annualized_volatility_pct": round(volatility, 2),
                "atr_pct": round(atr_pct, 2),
                "return_5d_pct": round(return_5d_pct, 2),
                "return_20d_pct": round(return_20d_pct, 2),
                "bullish_checks": bullish_points,
                "bearish_checks": bearish_points,
                "volume_ratio": round(volume_ratio, 2),
            },
            reasons=[f"Market regime: {regime} ({profile})"],
        )


class StockQualificationEngine(AnalysisEngine):
    name = "stock_qualification"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        history_count = len(candles)
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"))
        atr_pct = (atr_value / close * 100.0) if close > 0 else 0.0
        recent = candles.tail(20)
        average_volume = safe_float(recent["volume"].mean())
        average_turnover = safe_float((recent["close"] * recent["volume"]).mean())
        zero_volume_ratio = float((candles["volume"].tail(60) <= 0).mean())

        checks = {
            "history": history_count >= self.config.min_history,
            "liquidity": average_turnover >= self.config.min_average_turnover_egp,
            "atr_range": self.config.atr_min_pct <= atr_pct <= self.config.atr_max_pct,
            "volume_continuity": zero_volume_ratio <= 0.20,
            "valid_price": close > 0,
        }
        weights = {
            "history": 20.0,
            "liquidity": 30.0,
            "atr_range": 25.0,
            "volume_continuity": 15.0,
            "valid_price": 10.0,
        }
        score = sum(weights[key] for key, passed in checks.items() if passed)
        critical_checks = (
            checks["history"],
            checks["liquidity"],
            checks["atr_range"],
            checks["valid_price"],
        )
        qualified = score >= self.config.min_qualification_score and all(critical_checks)
        context["qualified"] = qualified
        context["atr_pct"] = atr_pct
        context["average_turnover_egp"] = average_turnover

        failed = [key for key, passed in checks.items() if not passed]
        return EngineResult(
            name=self.name,
            score=score,
            confidence=90.0 if history_count >= self.config.min_history else 55.0,
            status="complete" if qualified else "rejected",
            details={
                "qualified": qualified,
                "checks": checks,
                "history_count": history_count,
                "average_volume_20": round(average_volume, 2),
                "average_turnover_egp_20": round(average_turnover, 2),
                "liquidity_threshold_egp": round(
                    self.config.min_average_turnover_egp,
                    2,
                ),
                "atr_pct": round(atr_pct, 2),
                "zero_volume_ratio": round(zero_volume_ratio, 3),
            },
            reasons=[] if qualified else [f"Failed qualification: {', '.join(failed)}"],
        )
