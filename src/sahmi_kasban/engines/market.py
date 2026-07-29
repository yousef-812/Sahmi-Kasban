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
        slope_20 = safe_float(latest.get("trend_slope_20"))
        slope_60 = safe_float(latest.get("trend_slope_60"))
        r2_20 = safe_float(latest.get("trend_r2_20"))
        r2_60 = safe_float(latest.get("trend_r2_60"))
        adx_value = safe_float(latest.get("adx_14"))
        efficiency = safe_float(latest.get("price_efficiency_20"))
        volatility_20 = safe_float(latest.get("volatility_20d"))
        volatility_60 = safe_float(latest.get("volatility_60d"), volatility_20)
        annualized_volatility = volatility_20 * (252**0.5) * 100.0
        drawdown = safe_float(latest.get("drawdown_60d")) * 100.0
        volume_ratio = safe_float(latest.get("volume_ratio"))

        bullish_structure = close > sma_20 > sma_50 and slope_20 > 0 and slope_60 >= 0
        bearish_structure = close < sma_20 < sma_50 and slope_20 < 0 and slope_60 <= 0
        if bullish_structure and adx_value >= 18:
            regime = "bullish"
        elif bearish_structure and adx_value >= 18:
            regime = "bearish"
        else:
            regime = "sideways"

        score = 50.0
        score += max(-14.0, min(14.0, slope_20 * 35.0))
        score += max(-10.0, min(10.0, slope_60 * 28.0))
        score += 8.0 if close > sma_50 else -8.0
        score += (r2_20 - 0.5) * 10.0
        if adx_value >= 25:
            score += 6.0 if slope_20 > 0 else -6.0 if slope_20 < 0 else 0.0
        if annualized_volatility > 70:
            score -= 10.0
        elif annualized_volatility < 25 and slope_20 > 0:
            score += 4.0
        if volatility_60 > 0 and volatility_20 > volatility_60 * 1.5:
            score -= 6.0
        if drawdown < -20:
            score -= 10.0
        elif drawdown > -5 and slope_20 > 0:
            score += 3.0
        if volume_ratio >= 1.2 and slope_20 > 0:
            score += 4.0
        elif volume_ratio >= 1.2 and slope_20 < 0:
            score -= 4.0

        score = self.clamp(score)
        trend_quality = max(0.0, min(100.0, (r2_20 * 55.0 + r2_60 * 25.0 + efficiency * 20.0)))
        confidence = min(
            94.0,
            52.0 + trend_quality * 0.28 + min(adx_value, 40.0) * 0.35,
        )
        context["market_regime"] = regime
        context["annualized_volatility"] = annualized_volatility
        context["trend_quality"] = trend_quality
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "regime": regime,
                "scope": "instrument_only",
                "benchmark_supplied": False,
                "annualized_volatility_pct": round(annualized_volatility, 2),
                "volatility_ratio_20_60": round(
                    volatility_20 / volatility_60 if volatility_60 > 0 else 0.0,
                    3,
                ),
                "drawdown_60d_pct": round(drawdown, 2),
                "trend_slope_20_pct_per_bar": round(slope_20, 4),
                "trend_slope_60_pct_per_bar": round(slope_60, 4),
                "trend_r2_20": round(r2_20, 3),
                "trend_r2_60": round(r2_60, 3),
                "trend_quality": round(trend_quality, 2),
                "adx_14": round(adx_value, 2),
                "price_efficiency_20": round(efficiency, 3),
                "volume_ratio": round(volume_ratio, 2),
            },
            reasons=[
                f"Instrument price regime: {regime}",
                "No broad-market benchmark was supplied; this engine measures the stock regime only",
            ],
        )


class StockQualificationEngine(AnalysisEngine):
    name = "stock_qualification"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        history_count = len(candles)
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"))
        atr_pct = (atr_value / close * 100.0) if close > 0 else 0.0
        recent = candles.tail(min(60, history_count))
        average_volume = safe_float(recent["volume"].tail(20).mean())
        average_turnover = safe_float(
            (recent["close"].tail(20) * recent["volume"].tail(20)).mean()
        )
        zero_volume_ratio = float((recent["volume"] <= 0).mean())
        returns = recent["close"].pct_change().dropna()
        outlier_return_ratio = float((returns.abs() > 0.35).mean()) if not returns.empty else 1.0
        candle_integrity = (
            (recent["high"] >= recent[["open", "close"]].max(axis=1))
            & (recent["low"] <= recent[["open", "close"]].min(axis=1))
            & (recent["high"] >= recent["low"])
        )
        candle_integrity_ratio = float(candle_integrity.mean())
        duplicate_timestamp_ratio = 0.0
        if "timestamp" in recent.columns and recent["timestamp"].notna().any():
            duplicate_timestamp_ratio = float(recent["timestamp"].duplicated().mean())

        checks = {
            "history": history_count >= self.config.min_history,
            "share_liquidity": average_volume >= self.config.min_average_volume,
            "turnover_liquidity": average_turnover >= self.config.min_average_turnover,
            "atr_range": self.config.atr_min_pct <= atr_pct <= self.config.atr_max_pct,
            "volume_continuity": zero_volume_ratio <= 0.20,
            "candle_integrity": candle_integrity_ratio >= 0.98,
            "return_outliers": outlier_return_ratio <= 0.05,
            "timestamp_uniqueness": duplicate_timestamp_ratio == 0.0,
            "valid_price": close > 0,
        }
        weights = {
            "history": 12.0,
            "share_liquidity": 12.0,
            "turnover_liquidity": 18.0,
            "atr_range": 14.0,
            "volume_continuity": 10.0,
            "candle_integrity": 16.0,
            "return_outliers": 8.0,
            "timestamp_uniqueness": 5.0,
            "valid_price": 5.0,
        }
        score = sum(weights[key] for key, passed in checks.items() if passed)
        critical_checks = (
            checks["history"],
            checks["turnover_liquidity"],
            checks["atr_range"],
            checks["candle_integrity"],
            checks["valid_price"],
        )
        qualified = score >= self.config.min_qualification_score and all(critical_checks)
        context["qualified"] = qualified
        context["atr_pct"] = atr_pct
        context["average_turnover_20"] = average_turnover

        failed = [key for key, passed in checks.items() if not passed]
        confidence = min(
            98.0,
            58.0 + min(history_count, 250) / 8.0 + candle_integrity_ratio * 10.0,
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            status="complete" if qualified else "rejected",
            details={
                "qualified": qualified,
                "checks": checks,
                "history_count": history_count,
                "average_volume_20": round(average_volume, 2),
                "average_turnover_20": round(average_turnover, 2),
                "atr_pct": round(atr_pct, 2),
                "zero_volume_ratio": round(zero_volume_ratio, 3),
                "candle_integrity_ratio": round(candle_integrity_ratio, 3),
                "outlier_return_ratio": round(outlier_return_ratio, 3),
                "duplicate_timestamp_ratio": round(duplicate_timestamp_ratio, 3),
            },
            reasons=[] if qualified else [f"Failed qualification: {', '.join(failed)}"],
        )
