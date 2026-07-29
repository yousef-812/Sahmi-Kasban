from __future__ import annotations

import math

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult, TradePlan


class RiskEngine(AnalysisEngine):
    name = "risk"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        price = safe_float(latest["close"])
        atr_value = max(safe_float(latest.get("atr"), price * 0.02), price * 0.0025)
        volatility = safe_float(latest.get("volatility_20d"))
        average_volume = safe_float(latest.get("avg_volume_20"))
        volume_ratio = safe_float(latest.get("volume_ratio"))
        drawdown = safe_float(latest.get("drawdown_60d"))
        recent_returns = candles["close"].pct_change().tail(20).dropna()
        maximum_gap = safe_float(recent_returns.abs().max())
        average_turnover = safe_float(
            (candles["close"].tail(20) * candles["volume"].tail(20)).mean()
        )

        entry = price
        atr_stop = entry - atr_value * self.config.stop_atr_multiple
        recent_lows = candles["low"].tail(self.config.support_lookback)
        swing_support = safe_float(recent_lows.min(), atr_stop)
        structural_stop = swing_support - atr_value * 0.25
        stop_candidate = min(atr_stop, structural_stop) if structural_stop < entry else atr_stop
        maximum_distance = atr_value * self.config.max_stop_atr_multiple
        stop_floor = entry - maximum_distance
        stop_loss = max(0.01, stop_floor, stop_candidate)
        stop_basis = "atr_and_structure" if stop_loss < atr_stop else "atr"

        risk_per_share = max(entry - stop_loss, entry * 0.005)
        risk_budget = self.config.capital * self.config.risk_per_trade
        by_risk = int(risk_budget / risk_per_share)
        by_value = int(self.config.max_position_value / entry) if entry > 0 else 0
        by_liquidity = int(average_volume * self.config.liquidity_participation_rate)
        position_size = max(0, min(by_risk, by_value, by_liquidity))
        position_value = position_size * entry
        target_1 = entry + risk_per_share * self.config.target_1_r
        target_2 = entry + risk_per_share * self.config.target_2_r

        annualized_volatility = volatility * math.sqrt(252.0) * 100.0
        atr_pct = atr_value / price * 100.0 if price > 0 else 100.0
        volatility_risk = min(100.0, annualized_volatility / 85.0 * 100.0)
        atr_risk = min(100.0, atr_pct / max(self.config.atr_max_pct, 0.1) * 100.0)
        drawdown_risk = min(100.0, abs(min(drawdown, 0.0)) / 0.30 * 100.0)
        gap_risk = min(100.0, maximum_gap / 0.15 * 100.0)
        if average_turnover < self.config.min_average_turnover:
            liquidity_risk = 85.0
        elif volume_ratio < 0.65:
            liquidity_risk = 65.0
        elif volume_ratio < 0.90:
            liquidity_risk = 40.0
        else:
            liquidity_risk = 20.0
        total_risk = min(
            100.0,
            volatility_risk * 0.27
            + atr_risk * 0.20
            + drawdown_risk * 0.20
            + gap_risk * 0.15
            + liquidity_risk * 0.18,
        )
        score = 100.0 - total_risk

        plan = TradePlan(
            entry=round(entry, 4),
            stop_loss=round(stop_loss, 4),
            target_1=round(target_1, 4),
            target_2=round(target_2, 4),
            risk_per_share=round(risk_per_share, 4),
            reward_risk_1=round((target_1 - entry) / risk_per_share, 2),
            reward_risk_2=round((target_2 - entry) / risk_per_share, 2),
            position_size=position_size,
            position_value=round(position_value, 2),
            risk_amount=round(min(position_size * risk_per_share, risk_budget), 2),
        )
        context["trade_plan"] = plan
        context["risk_level"] = (
            "low" if total_risk < 35 else "medium" if total_risk < 60 else "high"
        )

        warnings: list[str] = []
        if position_size <= 0:
            warnings.append("Position size is zero under risk, value, or liquidity limits")
        if atr_pct > self.config.atr_max_pct:
            warnings.append("ATR exceeds configured maximum")
        if by_liquidity < min(by_risk, by_value):
            warnings.append("Position size reduced by market-liquidity participation cap")
        if maximum_gap > 0.10:
            warnings.append("Recent gap risk is elevated")
        confidence = min(
            95.0,
            60.0
            + min(len(candles), 200) / 10.0
            + (10.0 if average_turnover >= self.config.min_average_turnover else 0.0),
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "risk_level": context["risk_level"],
                "total_risk_pct": round(total_risk, 2),
                "risk_components": {
                    "annualized_volatility": round(volatility_risk, 2),
                    "atr": round(atr_risk, 2),
                    "drawdown": round(drawdown_risk, 2),
                    "gap": round(gap_risk, 2),
                    "liquidity": round(liquidity_risk, 2),
                },
                "annualized_volatility_pct": round(annualized_volatility, 2),
                "atr_pct": round(atr_pct, 2),
                "drawdown_60d_pct": round(drawdown * 100.0, 2),
                "maximum_gap_20d_pct": round(maximum_gap * 100.0, 2),
                "average_turnover_20": round(average_turnover, 2),
                "volume_ratio": round(volume_ratio, 2),
                "swing_support": round(swing_support, 4),
                "atr_stop": round(atr_stop, 4),
                "structural_stop": round(structural_stop, 4),
                "stop_basis": stop_basis,
                "position_caps": {
                    "by_risk": by_risk,
                    "by_value": by_value,
                    "by_liquidity": by_liquidity,
                },
                "liquidity_participation_rate": self.config.liquidity_participation_rate,
                "trade_plan": plan.to_dict(),
            },
            reasons=warnings,
        )
