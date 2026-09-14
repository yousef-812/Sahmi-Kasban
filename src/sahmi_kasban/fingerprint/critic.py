from __future__ import annotations

from typing import Any

from sahmi_kasban.ai.service import SahmiAIService
from sahmi_kasban.fingerprint.models import (
    AccumulationSweepPattern,
    AICriticEvaluation,
    TimeCyclePattern,
)


class AISignatureCritic:
    """AI Critic layer evaluating extracted stock patterns to prevent overfitting."""

    def __init__(self, ai_service: SahmiAIService | None = None) -> None:
        self.ai_service = ai_service or SahmiAIService()

    async def evaluate_signature(
        self,
        ticker: str,
        time_cycle: TimeCyclePattern,
        accumulation_sweep: AccumulationSweepPattern,
    ) -> AICriticEvaluation:
        try:
            result = await self.ai_service.evaluate_algorithmic_signature(
                ticker=ticker,
                time_cycle=time_cycle.to_dict(),
                accumulation_sweep=accumulation_sweep.to_dict(),
            )
            return AICriticEvaluation.from_dict(result)
        except Exception as exc:
            # Fallback deterministic evaluation if AI service is offline
            warnings: list[str] = []
            approved = True
            confidence = 65.0

            if time_cycle.stability_score < 40.0:
                warnings.append("Time cycle stability is low")
                confidence -= 10.0

            if accumulation_sweep.bounce_probability_pct < 50.0:
                warnings.append("Historical sweep bounce probability is below 50%")
                confidence -= 15.0

            if confidence < 40.0:
                approved = False

            return AICriticEvaluation(
                approved=approved,
                confidence=round(max(0.0, min(100.0, confidence)), 2),
                summary=f"Deterministic fallback critique for {ticker.upper()} (AI offline: {exc})",
                warnings=warnings,
            )
