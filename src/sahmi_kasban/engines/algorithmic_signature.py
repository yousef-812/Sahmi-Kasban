from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.fingerprint.models import StockAlgorithmicSignature
from sahmi_kasban.fingerprint.registry import StockSignatureRegistry
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class AlgorithmicSignatureEngine(AnalysisEngine):
    """Directional engine evaluating real-time price action against the stock's persistent signature."""

    name = "algorithmic_signature"

    def __init__(self, config=None, registry: StockSignatureRegistry | None = None) -> None:
        super().__init__(config)
        self.registry = registry or StockSignatureRegistry()

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        symbol = str(context.get("ticker", "")).strip().upper()
        signature = context.get("stock_signature")

        if not isinstance(signature, StockAlgorithmicSignature):
            signature = self.registry.get_signature(symbol)

        if signature is None or not signature.ai_critic.approved:
            return EngineResult(
                name=self.name,
                score=50.0,
                confidence=50.0,
                details={
                    "model_version": "algo-signature-v1.0",
                    "signature_found": signature is not None,
                    "approved_by_critic": signature.ai_critic.approved if signature else False,
                },
                reasons=["No approved stock signature available"],
            )

        tc = signature.time_cycle
        acc = signature.accumulation_sweep

        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        low = safe_float(latest["low"])

        prior_20 = candles.iloc[-21:-1] if len(candles) >= 21 else candles.iloc[:-1]
        prior_low = safe_float(prior_20["low"].min(), close) if not prior_20.empty else close

        sweep_depth_pct = (prior_low - low) / prior_low * 100.0 if prior_low > 0 else 0.0

        score = 50.0
        reasons: list[str] = []

        # 1. Time Cycle Alignment
        time_aligned = tc.next_window_in_sessions <= 3
        if time_aligned:
            score += 20.0 * (tc.stability_score / 100.0)
            reasons.append(
                f"Current session in predicted cycle window ({tc.next_window_in_sessions} sessions left)"
            )
        else:
            score += 5.0

        # 2. Accumulation & Sweep Pattern Alignment
        if low < prior_low and close > low:  # Liquidity sweep occurring
            diff_from_historical = abs(sweep_depth_pct - acc.avg_sweep_depth_pct)
            if diff_from_historical <= 1.5:  # Matches stock's specific sweep depth signature
                bounce_weight = acc.bounce_probability_pct / 100.0
                score += 25.0 * bounce_weight
                reasons.append(
                    f"Liquidity sweep matches historical depth ({sweep_depth_pct:.1f}% vs avg {acc.avg_sweep_depth_pct:.1f}%)"
                )
            else:
                score += 10.0

        score = self.clamp(score)
        confidence = min(
            95.0,
            (signature.overall_quality_score * 0.4)
            + (tc.stability_score * 0.3)
            + (signature.ai_critic.confidence * 0.3),
        )

        context["signature_conformance_score"] = score
        context["signature_time_aligned"] = time_aligned

        return EngineResult(
            name=self.name,
            score=score,
            confidence=round(confidence, 2),
            details={
                "model_version": "algo-signature-v1.0",
                "signature_found": True,
                "approved_by_critic": True,
                "dominant_cycle_sessions": tc.dominant_cycle_sessions,
                "cycle_stability_score": tc.stability_score,
                "next_window_in_sessions": tc.next_window_in_sessions,
                "current_sweep_depth_pct": round(sweep_depth_pct, 2),
                "historical_avg_sweep_depth_pct": acc.avg_sweep_depth_pct,
                "historical_bounce_probability_pct": acc.bounce_probability_pct,
                "overall_quality_score": signature.overall_quality_score,
            },
            reasons=reasons or ["Stock signature analysis completed"],
        )
