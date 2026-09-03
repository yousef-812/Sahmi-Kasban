from __future__ import annotations

import asyncio
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sahmi_kasban.ai import AIProviderError, SahmiAIService

from app.api.dependencies import CurrentUser, DatabaseSession
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider, MarketDataUnavailableError
from app.models import PredictionVerification
from app.schemas.prediction_verification import (
    PredictionStatsResponse,
    PredictionVerificationResponse,
    PredictionVerificationStatusResponse,
    PredictionVerificationSubmissionResponse,
)
from app.services.community_ai import get_community_ai_service
from app.services.prediction_evaluation import (
    PredictionMarketEvidenceError,
    PredictionNotEligibleError,
    PredictionNotFoundError,
    PredictionUnavailableError,
    calculate_prediction_score,
    deterministic_explanation,
    finalize_prediction_verification,
    get_prediction_stats,
    get_prediction_status,
    select_window_candles,
)
from app.services.wallet import get_wallet_account, points_to_coins

router = APIRouter(prefix="/community", tags=["prediction-verification"])
PredictionMarketProvider = Annotated[
    MarketDataProvider,
    Depends(get_market_data_provider),
]
PredictionAIService = Annotated[
    SahmiAIService,
    Depends(get_community_ai_service),
]


def _verification_response(
    verification: PredictionVerification,
) -> PredictionVerificationResponse:
    return PredictionVerificationResponse(
        id=verification.id,
        discussion_id=verification.discussion_id,
        score_bp=verification.score_bp,
        score_percent=round(verification.score_bp / 100, 2),
        strength=verification.strength,
        reward_points=verification.reward_points,
        reward_coins=points_to_coins(verification.reward_points),
        evidence=verification.evidence,
        verified_at=verification.verified_at,
    )


def _status_response(result) -> PredictionVerificationStatusResponse:
    return PredictionVerificationStatusResponse(
        discussion_id=result.discussion.id,
        state=result.state,
        eligible_at=result.window.eligible_at if result.window is not None else None,
        verification=(
            _verification_response(result.verification) if result.verification is not None else None
        ),
    )


def _not_eligible_detail(exc: PredictionNotEligibleError) -> str:
    return f"لم تنتهِ فترة التوقع بعد. سيكون التحقق متاحًا بعد {exc.eligible_at.isoformat()}."


def _safe_ai_explanation(
    *,
    ai_result: dict[str, Any],
) -> dict[str, Any]:
    matched_claims = ai_result.get("matched_claims")
    failed_claims = ai_result.get("failed_claims")
    return {
        "source": "ai",
        "reason": str(ai_result.get("reason") or "").strip(),
        "matched_claims": [str(item)[:300] for item in matched_claims[:20]]
        if isinstance(matched_claims, list)
        else [],
        "failed_claims": [str(item)[:300] for item in failed_claims[:20]]
        if isinstance(failed_claims, list)
        else [],
        "reward_ignored": True,
    }


async def _load_prediction_score(
    *,
    market_provider: MarketDataProvider,
    discussion,
    window,
):
    last_error: MarketDataUnavailableError | PredictionMarketEvidenceError | None = None
    for attempt in range(2):
        try:
            series = await market_provider.get_history(
                discussion.ticker,
                period="6mo",
                interval="1d",
            )
            candles = select_window_candles(series, window=window)
            return calculate_prediction_score(
                prediction=discussion.frozen_prediction,
                candles=candles,
                window=window,
                ticker=discussion.ticker,
            )
        except (MarketDataUnavailableError, PredictionMarketEvidenceError) as exc:
            last_error = exc
            if attempt == 0:
                await asyncio.sleep(0.75)
    assert last_error is not None
    raise last_error


@router.get(
    "/discussions/{discussion_id}/verification",
    response_model=PredictionVerificationStatusResponse,
)
def prediction_verification_status(
    discussion_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> PredictionVerificationStatusResponse:
    try:
        result = get_prediction_status(
            db,
            discussion_id=discussion_id,
            user_id=current_user.id,
        )
    except PredictionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _status_response(result)


@router.post(
    "/discussions/{discussion_id}/verification",
    response_model=PredictionVerificationSubmissionResponse,
)
async def verify_prediction(
    discussion_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
    market_provider: PredictionMarketProvider,
    ai_service: PredictionAIService,
) -> PredictionVerificationSubmissionResponse:
    try:
        current_status = get_prediction_status(
            db,
            discussion_id=discussion_id,
            user_id=current_user.id,
        )
    except PredictionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if current_status.verification is not None:
        account = get_wallet_account(db, current_user.id)
        return PredictionVerificationSubmissionResponse(
            verification=_verification_response(current_status.verification),
            balance_points=account.balance_points,
            balance_coins=points_to_coins(account.balance_points),
            idempotent=True,
        )
    if current_status.state == "unavailable" or current_status.window is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="هذه المناقشة غير مؤهلة للتحقق.",
        )
    if current_status.state == "waiting":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "لم تنتهِ فترة التوقع بعد. سيكون التحقق متاحًا بعد "
                f"{current_status.window.eligible_at.isoformat()}."
            ),
        )

    try:
        score = await _load_prediction_score(
            market_provider=market_provider,
            discussion=current_status.discussion,
            window=current_status.window,
        )
    except (MarketDataUnavailableError, PredictionMarketEvidenceError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "انتهت فترة التوقع، لكن مزود السوق لم يثبت إغلاق كل الجلسات بعد. "
                "لم تُحسب نتيجة جزئية ولم تُصرف مكافأة؛ أعد المحاولة بعد قليل."
            ),
        ) from exc

    try:
        ai_result = await ai_service.verify_prediction(
            prediction=current_status.discussion.frozen_prediction,
            market_outcome=score.market_outcome,
        )
        explanation = _safe_ai_explanation(ai_result=ai_result)
    except AIProviderError:
        explanation = {
            "source": "deterministic_fallback",
            "reason": deterministic_explanation(score),
            "matched_claims": [],
            "failed_claims": [],
            "reward_ignored": True,
        }

    try:
        result = finalize_prediction_verification(
            db,
            discussion_id=discussion_id,
            user_id=current_user.id,
            score=score,
            explanation=explanation,
        )
        db.commit()
    except PredictionNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PredictionNotEligibleError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_not_eligible_detail(exc),
        ) from exc
    except PredictionUnavailableError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return PredictionVerificationSubmissionResponse(
        verification=_verification_response(result.verification),
        balance_points=result.balance_points,
        balance_coins=points_to_coins(result.balance_points),
        idempotent=result.idempotent,
    )


@router.get(
    "/predictions/stats/mine",
    response_model=PredictionStatsResponse,
)
def my_prediction_stats(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> PredictionStatsResponse:
    prediction_stats = get_prediction_stats(db, user_id=current_user.id)
    accuracy_percent = (
        round(
            prediction_stats.accepted_predictions / prediction_stats.verified_predictions * 100,
            2,
        )
        if prediction_stats.verified_predictions
        else 0.0
    )
    return PredictionStatsResponse(
        verified_predictions=prediction_stats.verified_predictions,
        accepted_predictions=prediction_stats.accepted_predictions,
        accuracy_percent=accuracy_percent,
        average_score_percent=round(prediction_stats.average_score_bp / 100, 2),
        total_reward_points=prediction_stats.total_reward_points,
        total_reward_coins=points_to_coins(prediction_stats.total_reward_points),
    )
