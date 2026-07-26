from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any
from uuid import UUID

from sahmi_kasban.ai import AIProviderError, SahmiAIService
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Discussion, DiscussionModerationEvent
from app.services.community import (
    CommunityConflictError,
    DiscussionNotFoundError,
    apply_moderation_decision,
)

_ALLOWED_DIRECTIONS = {"up", "down", "neutral"}
_AI_REASON_CODES = {
    "off_topic",
    "spam",
    "abuse",
    "misleading",
    "profit_guarantee",
    "advertisement",
    "contact_info",
    "external_link",
    "prediction_not_clear",
}


@dataclass(frozen=True)
class CommunityAIReviewResult:
    discussion: Discussion
    ai_status: str


@lru_cache
def get_community_ai_service() -> SahmiAIService:
    return SahmiAIService()


def _clean_text(value: object, *, max_length: int) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned[:max_length]


def _normalize_direction(value: object) -> str:
    direction = str(value or "unknown").strip().lower()
    aliases = {
        "rise": "up",
        "bullish": "up",
        "صعود": "up",
        "هبوط": "down",
        "fall": "down",
        "bearish": "down",
        "محايد": "neutral",
        "sideways": "neutral",
    }
    direction = aliases.get(direction, direction)
    return direction if direction in _ALLOWED_DIRECTIONS else "unknown"


def _normalize_target_price(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        price = float(value)
    except (TypeError, ValueError):
        return None
    if not 0 < price < 10_000_000:
        return None
    return round(price, 4)


def _normalize_specificity(value: object) -> float:
    try:
        specificity = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(min(max(specificity, 0.0), 1.0), 4)


def _normalize_claims(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    claims: list[str] = []
    for item in value[:10]:
        cleaned = _clean_text(item, max_length=300)
        if cleaned and cleaned not in claims:
            claims.append(cleaned)
    return claims


def normalize_frozen_prediction(
    discussion: Discussion,
    extracted: dict[str, Any],
    *,
    moment: datetime | None = None,
) -> dict[str, Any]:
    direction = _normalize_direction(extracted.get("direction"))
    if direction == "unknown":
        raise ValueError("Prediction direction is not clear")

    source_text = f"{discussion.title}\n{discussion.content}"
    frozen_at = moment or datetime.now(UTC)
    return {
        "version": 1,
        "ticker": discussion.ticker,
        "direction": direction,
        "target_price": _normalize_target_price(extracted.get("target_price")),
        "period_type": discussion.period_type,
        "deadline": _clean_text(extracted.get("deadline"), max_length=120),
        "claims": _normalize_claims(extracted.get("claims")),
        "specificity": _normalize_specificity(extracted.get("specificity")),
        "source_text_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "frozen_at": frozen_at.isoformat(),
    }


def _ai_rejection_code(moderation: dict[str, Any]) -> str:
    flags = moderation.get("flags")
    if isinstance(flags, list):
        for raw_flag in flags:
            flag = str(raw_flag).strip().lower()
            if flag in _AI_REASON_CODES:
                return flag
    category = str(moderation.get("category", "")).strip().lower()
    if category in _AI_REASON_CODES:
        return category
    return "ai_rejected"


def _safe_moderation_payload(moderation: dict[str, Any]) -> dict[str, Any]:
    flags = moderation.get("flags")
    return {
        "approved": bool(moderation.get("approved", False)),
        "category": _clean_text(moderation.get("category"), max_length=80) or "unknown",
        "reason": _clean_text(moderation.get("reason"), max_length=500)
        or "تعذر تحديد سبب واضح",
        "flags": [str(item)[:80] for item in flags[:20]]
        if isinstance(flags, list)
        else [],
    }


def record_ai_review_failure(
    db: Session,
    *,
    discussion_id: UUID,
    error_code: str = "provider_unavailable",
    moment: datetime | None = None,
) -> Discussion:
    attempted_at = moment or datetime.now(UTC)
    discussion = db.scalar(
        select(Discussion)
        .where(Discussion.id == discussion_id)
        .with_for_update()
    )
    if discussion is None:
        raise DiscussionNotFoundError("Discussion does not exist")
    if discussion.status != "pending_review":
        return discussion

    result = dict(discussion.moderation_result)
    previous_ai = result.get("ai")
    attempts = 0
    if isinstance(previous_ai, dict):
        try:
            attempts = int(previous_ai.get("attempts", 0))
        except (TypeError, ValueError):
            attempts = 0
    result["ai"] = {
        "status": "failed",
        "error_code": error_code,
        "attempts": attempts + 1,
        "attempted_at": attempted_at.isoformat(),
    }
    result["review_stage"] = "awaiting_ai_retry"
    discussion.moderation_result = result
    db.add(
        DiscussionModerationEvent(
            discussion_id=discussion.id,
            actor_type="ai",
            actor_user_id=None,
            action="ai_failed",
            reason_code=error_code,
            details={"attempt": attempts + 1},
        )
    )
    db.flush()
    return discussion


async def review_pending_discussion(
    db: Session,
    *,
    discussion_id: UUID,
    ai_service: SahmiAIService,
    moment: datetime | None = None,
) -> CommunityAIReviewResult:
    discussion = db.get(Discussion, discussion_id)
    if discussion is None:
        raise DiscussionNotFoundError("Discussion does not exist")
    if discussion.status != "pending_review":
        return CommunityAIReviewResult(discussion=discussion, ai_status="already_final")

    rules = discussion.moderation_result.get("rules", {})
    if not isinstance(rules, dict) or not rules.get("passed", False):
        return CommunityAIReviewResult(discussion=discussion, ai_status="rules_not_passed")

    review_text = (
        f"السهم المختار: {discussion.ticker}\n"
        f"مدة التوقع: {discussion.period_type}\n"
        f"العنوان: {discussion.title}\n"
        f"المحتوى: {discussion.content}"
    )
    try:
        raw_moderation = await ai_service.moderate_discussion(review_text)
        moderation = _safe_moderation_payload(raw_moderation)
        if not moderation["approved"]:
            rejection_code = _ai_rejection_code(raw_moderation)
            reviewed = apply_moderation_decision(
                db,
                discussion_id=discussion.id,
                decision="reject",
                actor_type="ai",
                reason_code=rejection_code,
                moderation_details=moderation,
                moment=moment,
            )
            return CommunityAIReviewResult(discussion=reviewed, ai_status="rejected")

        extracted = await ai_service.extract_prediction(review_text)
        try:
            frozen_prediction = normalize_frozen_prediction(
                discussion,
                extracted,
                moment=moment,
            )
        except ValueError:
            reviewed = apply_moderation_decision(
                db,
                discussion_id=discussion.id,
                decision="reject",
                actor_type="ai",
                reason_code="prediction_not_clear",
                moderation_details={
                    **moderation,
                    "prediction_extraction": "direction_missing",
                },
                moment=moment,
            )
            return CommunityAIReviewResult(discussion=reviewed, ai_status="rejected")

        reviewed = apply_moderation_decision(
            db,
            discussion_id=discussion.id,
            decision="accept",
            actor_type="ai",
            moderation_details=moderation,
            frozen_prediction=frozen_prediction,
            moment=moment,
        )
        return CommunityAIReviewResult(discussion=reviewed, ai_status="published")
    except AIProviderError:
        failed = record_ai_review_failure(
            db,
            discussion_id=discussion.id,
            moment=moment,
        )
        return CommunityAIReviewResult(discussion=failed, ai_status="provider_failed")
    except CommunityConflictError as exc:
        db.rollback()
        final = db.get(Discussion, discussion_id)
        if final is None:
            raise DiscussionNotFoundError("Discussion does not exist") from exc
        return CommunityAIReviewResult(discussion=final, ai_status="race_resolved")
