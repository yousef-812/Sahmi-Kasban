from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult

ELITE_MIN_DIRECTIONAL_SCORE = 80.0
ELITE_MIN_CONFIDENCE = 70.0
BALANCED_MAX_RETURN_20D_PCT = 30.0
BALANCED_BASE_MAX_ATR_PCT = 4.5
BALANCED_BASE_MAX_TOTAL_RISK_PCT = 30.0
AGGRESSIVE_MIN_RETURN_20D_PCT = 5.0
AGGRESSIVE_MAX_RETURN_20D_PCT = 45.0
AGGRESSIVE_MAX_RETURN_5D_PCT = 15.0
AGGRESSIVE_MIN_BREAKOUT_PCT = 2.0
AGGRESSIVE_MAX_BREAKOUT_PCT = 12.0
AGGRESSIVE_MIN_VOLUME_RATIO = 2.0
AGGRESSIVE_MIN_TURNOVER_EGP = 5_000_000.0
ELITE_MAX_ZERO_VOLUME_RATIO = 0.10
AGGRESSIVE_MAX_ZERO_VOLUME_RATIO = 0.05


def _liquidity_tier(average_turnover_egp: float) -> str:
    if average_turnover_egp >= 20_000_000:
        return "high"
    if average_turnover_egp >= 5_000_000:
        return "medium"
    return "basic"


def _adaptive_limits(*, liquidity_tier: str, market_regime: str) -> dict[str, float]:
    balanced_atr = BALANCED_BASE_MAX_ATR_PCT
    balanced_risk = BALANCED_BASE_MAX_TOTAL_RISK_PCT
    aggressive_atr = 5.0
    aggressive_risk = 35.0

    if liquidity_tier == "medium":
        balanced_atr += 0.5
        balanced_risk += 2.5
        aggressive_atr = 5.5
        aggressive_risk = 40.0
    elif liquidity_tier == "high":
        balanced_atr += 1.0
        balanced_risk += 5.0
        aggressive_atr = 6.0
        aggressive_risk = 42.5

    if market_regime == "bearish":
        balanced_atr -= 0.5
        balanced_risk -= 2.5
        aggressive_atr -= 1.0
        aggressive_risk -= 5.0
    elif market_regime == "bullish":
        balanced_atr += 0.25

    return {
        "balanced_max_atr_pct": round(max(3.5, balanced_atr), 2),
        "balanced_max_total_risk_pct": round(max(25.0, balanced_risk), 2),
        "aggressive_max_atr_pct": round(max(5.0, aggressive_atr), 2),
        "aggressive_max_total_risk_pct": round(max(35.0, aggressive_risk), 2),
    }


def _weighted_score(checks: Mapping[str, bool], weights: Mapping[str, float]) -> float:
    return sum(weights[name] for name, passed in checks.items() if passed)


class OpportunityQualityEngine(AnalysisEngine):
    """Classify high-ranked BUY setups into balanced or aggressive elite profiles.

    Core v2.4 adaptively limits risk and atr while securing breakout momentum.
    """

    name = "opportunity_quality"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest.get("close"))
        return_20d_pct = safe_float(latest.get("return_20d")) * 100.0
        return_5d_pct = 0.0
        if len(candles) >= 6:
            close_5d = safe_float(candles.iloc[-6].get("close"))
            if close_5d > 0:
                return_5d_pct = (close / close_5d - 1.0) * 100.0

        prior = candles.iloc[-21:-1] if len(candles) >= 21 else candles.iloc[:-1]
        prior_high = safe_float(prior["high"].max()) if not prior.empty else close
        breakout_pct = (close / prior_high - 1.0) * 100.0 if prior_high > 0 else 0.0
        volume = safe_float(latest.get("volume"))
        average_volume = safe_float(latest.get("avg_volume_20"), volume)
        volume_ratio = volume / average_volume if average_volume > 0 else 0.0
        rsi = safe_float(latest.get("rsi"), 50.0)

        signal = str(context.get("signal", "WATCH")).upper()
        qualified = bool(context.get("qualified", False))
        final_score = safe_float(context.get("final_score"))
        confidence = safe_float(context.get("aggregate_confidence"))
        atr_pct = safe_float(context.get("atr_pct"))
        total_risk_pct = safe_float(context.get("total_risk_pct"))
        zero_volume_ratio = safe_float(context.get("zero_volume_ratio"))
        average_turnover_egp = safe_float(context.get("average_turnover_egp"))
        market_regime = str(context.get("market_regime", ""))
        market_regime_profile = str(context.get("market_regime_profile", market_regime))
        timeframe_alignment = str(context.get("timeframe_alignment", ""))
        risk_level = str(context.get("risk_level", ""))
        bullish_count = int(safe_float(context.get("bullish_engine_count")))
        bearish_count = int(safe_float(context.get("bearish_engine_count")))
        directional_conflict = bool(context.get("directional_conflict", False))

        liquidity_tier = _liquidity_tier(average_turnover_egp)
        limits = _adaptive_limits(
            liquidity_tier=liquidity_tier,
            market_regime=market_regime,
        )
        common_checks: dict[str, bool] = {
            "buy_signal": signal == "BUY",
            "qualified": qualified,
            "directional_score": final_score >= ELITE_MIN_DIRECTIONAL_SCORE,
            "aggregate_confidence": confidence >= ELITE_MIN_CONFIDENCE,
            "directional_consensus": (
                bullish_count >= 4 and bearish_count == 0 and not directional_conflict
            ),
            "bullish_market_regime": market_regime == "bullish",
            "bullish_timeframe_alignment": timeframe_alignment == "bullish",
        }
        balanced_checks = {
            **common_checks,
            "momentum_not_overextended": return_20d_pct <= BALANCED_MAX_RETURN_20D_PCT,
            "atr_controlled": 0 < atr_pct <= limits["balanced_max_atr_pct"],
            "risk_controlled": (
                risk_level != "high"
                and total_risk_pct <= limits["balanced_max_total_risk_pct"]
            ),
            "trading_continuity": zero_volume_ratio <= ELITE_MAX_ZERO_VOLUME_RATIO,
        }
        aggressive_checks = {
            **common_checks,
            "liquidity_supports_aggressive_profile": (
                average_turnover_egp >= AGGRESSIVE_MIN_TURNOVER_EGP
            ),
            "breakout_confirmed": (
                AGGRESSIVE_MIN_BREAKOUT_PCT
                <= breakout_pct
                <= AGGRESSIVE_MAX_BREAKOUT_PCT
            ),
            "volume_confirmation": volume_ratio >= AGGRESSIVE_MIN_VOLUME_RATIO,
            "momentum_window": (
                AGGRESSIVE_MIN_RETURN_20D_PCT
                <= return_20d_pct
                <= AGGRESSIVE_MAX_RETURN_20D_PCT
                and 0 < return_5d_pct <= AGGRESSIVE_MAX_RETURN_5D_PCT
                and return_20d_pct >= 1.3 * return_5d_pct
            ),
            "rsi_not_exhausted": 50 <= rsi <= 82,
            "atr_in_aggressive_band": 0 < atr_pct <= limits["aggressive_max_atr_pct"],
            "risk_within_aggressive_budget": (
                risk_level != "high"
                and total_risk_pct <= limits["aggressive_max_total_risk_pct"]
            ),
            "aggressive_trading_continuity": (
                zero_volume_ratio <= AGGRESSIVE_MAX_ZERO_VOLUME_RATIO
            ),
        }
        balanced_weights: Mapping[str, float] = {
            "buy_signal": 8.0,
            "qualified": 8.0,
            "directional_score": 14.0,
            "aggregate_confidence": 10.0,
            "directional_consensus": 12.0,
            "bullish_market_regime": 8.0,
            "bullish_timeframe_alignment": 8.0,
            "momentum_not_overextended": 14.0,
            "atr_controlled": 10.0,
            "risk_controlled": 6.0,
            "trading_continuity": 2.0,
        }
        aggressive_weights: Mapping[str, float] = {
            "buy_signal": 6.0,
            "qualified": 6.0,
            "directional_score": 10.0,
            "aggregate_confidence": 8.0,
            "directional_consensus": 10.0,
            "bullish_market_regime": 8.0,
            "bullish_timeframe_alignment": 8.0,
            "liquidity_supports_aggressive_profile": 8.0,
            "breakout_confirmed": 10.0,
            "volume_confirmation": 8.0,
            "momentum_window": 6.0,
            "rsi_not_exhausted": 4.0,
            "atr_in_aggressive_band": 4.0,
            "risk_within_aggressive_budget": 2.0,
            "aggressive_trading_continuity": 2.0,
        }

        balanced_failed = [name for name, passed in balanced_checks.items() if not passed]
        aggressive_failed = [name for name, passed in aggressive_checks.items() if not passed]
        balanced_ready = not balanced_failed
        aggressive_ready = not aggressive_failed
        selected_profile = (
            "balanced" if balanced_ready else "aggressive" if aggressive_ready else "none"
        )
        balanced_score = _weighted_score(balanced_checks, balanced_weights)
        aggressive_score = _weighted_score(aggressive_checks, aggressive_weights)
        readiness_score = max(balanced_score, aggressive_score)
        engine_ready = selected_profile != "none"
        selected_failed = (
            []
            if engine_ready
            else balanced_failed
        )

        return EngineResult(
            name=self.name,
            score=readiness_score,
            confidence=92.0 if engine_ready else 76.0,
            status="complete" if engine_ready else "rejected",
            details={
                "model_version": "elite-quality-v2.4-regime-adaptive",
                "engine_ready": engine_ready,
                "selected_profile": selected_profile,
                "balanced_ready": balanced_ready,
                "aggressive_ready": aggressive_ready,
                "readiness_score": round(readiness_score, 2),
                "balanced_readiness_score": round(balanced_score, 2),
                "aggressive_readiness_score": round(aggressive_score, 2),
                "recommended_position_multiplier": (
                    0.5 if selected_profile == "aggressive" else 1.0
                ),
                "checks": (
                    balanced_checks if selected_profile != "aggressive" else aggressive_checks
                ),
                "failed_checks": selected_failed,
                "balanced_checks": balanced_checks,
                "balanced_failed_checks": balanced_failed,
                "aggressive_checks": aggressive_checks,
                "aggressive_failed_checks": aggressive_failed,
                "adaptive_limits": limits,
                "thresholds": {
                    "min_directional_score": ELITE_MIN_DIRECTIONAL_SCORE,
                    "min_confidence": ELITE_MIN_CONFIDENCE,
                    "balanced_max_return_20d_pct": BALANCED_MAX_RETURN_20D_PCT,
                    "aggressive_return_20d_pct": [
                        AGGRESSIVE_MIN_RETURN_20D_PCT,
                        AGGRESSIVE_MAX_RETURN_20D_PCT,
                    ],
                    "aggressive_max_return_5d_pct": AGGRESSIVE_MAX_RETURN_5D_PCT,
                    "aggressive_breakout_pct": [
                        AGGRESSIVE_MIN_BREAKOUT_PCT,
                        AGGRESSIVE_MAX_BREAKOUT_PCT,
                    ],
                    "aggressive_min_volume_ratio": AGGRESSIVE_MIN_VOLUME_RATIO,
                    "aggressive_min_turnover_egp": AGGRESSIVE_MIN_TURNOVER_EGP,
                    "balanced_max_zero_volume_ratio": ELITE_MAX_ZERO_VOLUME_RATIO,
                    "aggressive_max_zero_volume_ratio": AGGRESSIVE_MAX_ZERO_VOLUME_RATIO,
                },
                "metrics": {
                    "final_score": round(final_score, 2),
                    "aggregate_confidence": round(confidence, 2),
                    "return_20d_pct": round(return_20d_pct, 2),
                    "return_5d_pct": round(return_5d_pct, 2),
                    "breakout_pct": round(breakout_pct, 2),
                    "volume_ratio": round(volume_ratio, 2),
                    "rsi": round(rsi, 2),
                    "atr_pct": round(atr_pct, 2),
                    "total_risk_pct": round(total_risk_pct, 2),
                    "average_turnover_egp": round(average_turnover_egp, 2),
                    "liquidity_tier": liquidity_tier,
                    "zero_volume_ratio": round(zero_volume_ratio, 3),
                    "market_regime": market_regime,
                    "market_regime_profile": market_regime_profile,
                    "timeframe_alignment": timeframe_alignment,
                    "risk_level": risk_level,
                    "bullish_engine_count": bullish_count,
                    "bearish_engine_count": bearish_count,
                },
            },
            reasons=(
                [f"Elite {selected_profile} quality gates passed"]
                if engine_ready
                else [f"Balanced elite gate failed: {name}" for name in balanced_failed]
                + [f"Aggressive elite gate failed: {name}" for name in aggressive_failed]
            ),
        )
