from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult, TradePlan

SHORT_HORIZON_SESSIONS = 5


class RiskEngine(AnalysisEngine):
    name = "risk"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        price = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"), price * 0.02)
        volatility = safe_float(latest.get("volatility_20d"))
        average_volume = safe_float(latest.get("avg_volume_20"))
        volume = safe_float(latest.get("volume"))
        volume_ratio = volume / average_volume if average_volume > 0 else 0.0
        atr_pct = atr_value / price * 100.0 if price > 0 else 100.0

        prior = candles.iloc[-21:-1] if len(candles) >= 21 else candles.iloc[:-1]
        prior_high = safe_float(prior["high"].max()) if not prior.empty else price
        breakout_pct = (price / prior_high - 1.0) * 100.0 if prior_high > 0 else 0.0
        aggressive_breakout = (
            0.5 <= breakout_pct <= 12.0
            and volume_ratio >= 1.5
            and atr_pct >= 3.0
        )

        entry = price

        market_regime = str(context.get("market_regime", "sideways"))
        market_volatility = safe_float(context.get("annualized_volatility"), 50.0)

        base_atr_multiple = self.config.stop_atr_multiple

        if market_regime == "sideways" or market_volatility < 40.0:
            adaptive_atr_multiple = max(1.5, base_atr_multiple - 0.5)
        elif market_regime in ("speculative_bullish", "risk_off_volatile") or market_volatility > 65.0:
            adaptive_atr_multiple = min(3.0, base_atr_multiple + 0.5)
        else:
            adaptive_atr_multiple = base_atr_multiple

        stop_loss = max(0.01, entry - atr_value * adaptive_atr_multiple)
        risk_per_share = max(entry - stop_loss, entry * 0.005)
        risk_amount = self.config.capital * self.config.risk_per_trade
        by_risk = int(risk_amount / risk_per_share)
        by_value = int(self.config.max_position_value / entry) if entry > 0 else 0
        position_size = max(0, min(by_risk, by_value))
        position_value = position_size * entry

        target_1_r = self.config.target_1_r
        target_2_r = self.config.target_2_r
        plan_style = "balanced_5_session"
        if aggressive_breakout:
            target_1_r = max(target_1_r, 1.25)
            target_2_r = max(target_2_r, 2.0)
            plan_style = "aggressive_breakout_5_session"
        target_1 = entry + risk_per_share * target_1_r
        target_2 = entry + risk_per_share * target_2_r

        liquidity_risk = 35.0 if volume_ratio < 0.7 else 20.0 if volume_ratio < 1.0 else 10.0
        volatility_risk = min(60.0, volatility * 1000.0)
        atr_risk = min(40.0, atr_pct * 5.0)
        total_risk = min(
            100.0,
            volatility_risk * 0.45 + atr_risk * 0.35 + liquidity_risk * 0.20,
        )
        score = 100.0 - total_risk

        plan = TradePlan(
            entry=round(entry, 4),
            stop_loss=round(stop_loss, 4),
            target_1=round(target_1, 4),
            target_2=round(target_2, 4),
            risk_per_share=round(risk_per_share, 4),
            reward_risk_1=round(target_1_r, 2),
            reward_risk_2=round(target_2_r, 2),
            position_size=position_size,
            position_value=round(position_value, 2),
            risk_amount=round(min(position_size * risk_per_share, risk_amount), 2),
        )
        context["trade_plan"] = plan
        context["trade_plan_style"] = plan_style
        context["risk_level"] = (
            "low" if total_risk < 35 else "medium" if total_risk < 60 else "high"
        )

        warnings: list[str] = []
        if position_size <= 0:
            warnings.append("Position size is zero under current risk limits")
        if atr_pct > self.config.atr_max_pct:
            warnings.append("ATR exceeds configured maximum")
        return EngineResult(
            name=self.name,
            score=score,
            confidence=88.0,
            details={
                "model_version": "risk-plan-v2.4-adaptive-atr",
                "risk_level": context["risk_level"],
                "total_risk_pct": round(total_risk, 2),
                "atr_pct": round(atr_pct, 2),
                "volume_ratio": round(volume_ratio, 2),
                "breakout_pct": round(breakout_pct, 2),
                "plan_style": plan_style,
                "horizon_sessions": SHORT_HORIZON_SESSIONS,
                "target_model": "atr_reward_targets_for_5_sessions",
                "base_atr_multiple": base_atr_multiple,
                "adaptive_atr_multiple": round(adaptive_atr_multiple, 2),
                "market_regime_context": market_regime,
                "recommended_position_multiplier": (
                    0.5 if aggressive_breakout else 1.0
                ),
                "trade_plan": plan.to_dict(),
            },
            reasons=warnings,
        )
