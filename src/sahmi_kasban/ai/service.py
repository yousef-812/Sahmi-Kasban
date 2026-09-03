from __future__ import annotations

import json
import re
from typing import Any

from sahmi_kasban.ai.client import AIChatClient, AIProviderError
from sahmi_kasban.ai.prompts import (
    DISCUSSION_MODERATION_SYSTEM_PROMPT,
    PERSONA_POST_GENERATION_SYSTEM_PROMPT,
    PREDICTION_EXTRACTION_SYSTEM_PROMPT,
    PREDICTION_VERIFICATION_SYSTEM_PROMPT,
    STOCK_ANALYSIS_SYSTEM_PROMPT,
)


class SahmiAIService:
    """High-level AI operations used by the future API and Flutter application."""

    def __init__(self, client: AIChatClient | None = None) -> None:
        self.client = client or AIChatClient()

    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict[str, Any],
        language: str = "ar",
    ) -> str:
        user_payload = {
            "ticker": ticker.upper(),
            "language": language,
            "analysis": analysis_payload,
        }
        return await self.client.chat(
            [
                {"role": "system", "content": STOCK_ANALYSIS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False, default=str),
                },
            ]
        )

    async def moderate_discussion(self, text: str) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=DISCUSSION_MODERATION_SYSTEM_PROMPT,
            payload={"discussion": text},
        )
        result.setdefault("approved", False)
        result.setdefault("category", "unknown")
        result.setdefault("reason", "تعذر تحديد سبب واضح")
        result.setdefault("flags", [])
        return result

    async def extract_prediction(self, text: str) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=PREDICTION_EXTRACTION_SYSTEM_PROMPT,
            payload={"discussion": text},
        )
        result.setdefault("ticker", None)
        result.setdefault("direction", "unknown")
        result.setdefault("target_price", None)
        result.setdefault("deadline", None)
        result.setdefault("claims", [])
        result.setdefault("specificity", 0.0)
        return result

    async def verify_prediction(
        self,
        *,
        prediction: dict[str, Any],
        market_outcome: dict[str, Any],
    ) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=PREDICTION_VERIFICATION_SYSTEM_PROMPT,
            payload={
                "prediction": prediction,
                "market_outcome": market_outcome,
            },
        )
        allowed_rewards = {
            "rejected": 0.0,
            "weak": 0.5,
            "strong": 1.0,
            "very_strong": 2.0,
        }
        level = str(result.get("level", "rejected"))
        if level not in allowed_rewards:
            level = "rejected"
        result["level"] = level
        result["reward_coins"] = allowed_rewards[level]
        result.setdefault("matched_claims", [])
        result.setdefault("failed_claims", [])
        result.setdefault("reason", "")
        return result

    async def generate_community_persona_post(
        self,
        *,
        persona_name: str,
        persona_traits: str,
        ticker: str,
        stock_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=PERSONA_POST_GENERATION_SYSTEM_PROMPT,
            payload={
                "persona_name": persona_name,
                "persona_traits": persona_traits,
                "ticker": ticker.upper(),
                "stock_analysis": stock_analysis,
            },
        )
        result.setdefault("title", f"رأيي في سهم {ticker.upper()}")
        result.setdefault("content", f"شايف حركة جيدة في سهم {ticker.upper()} الفترة دي.")
        result.setdefault("direction", "up")
        return result

    async def _chat_json(
        self,
        *,
        system_prompt: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        content = await self.client.chat(
            [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False, default=str),
                },
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return self._parse_json_object(content)

    @staticmethod
    def _parse_json_object(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise AIProviderError("AI response did not contain a JSON object") from exc
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError as nested_exc:
                raise AIProviderError("AI response contained invalid JSON") from nested_exc
        if not isinstance(parsed, dict):
            raise AIProviderError("AI JSON response must be an object")
        return parsed
