from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sahmi_kasban.ai import SahmiAIService
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import User
from app.services.community_ai import get_community_ai_service
from app.services.referral import ensure_user_referral_code
from app.services.wallet import InsufficientBalanceError, debit_points

router = APIRouter(prefix="/ai-copilot", tags=["ai_copilot"])
CommunityAIService = Annotated[SahmiAIService, Depends(get_community_ai_service)]

AI_COPILOT_COST_POINTS = 50  # 0.5 coins
REQUIRED_REFERRALS_COUNT = 5


class AiCopilotQueryRequest(BaseModel):
    ticker: str | None = Field(default=None, max_length=24)
    question: str = Field(min_length=3, max_length=1000)


class AiCopilotQueryResponse(BaseModel):
    answer: str
    ticker: str | None
    coins_deducted: float = 0.5


@router.post("/query", response_model=AiCopilotQueryResponse)
def query_ai_copilot(
    body: AiCopilotQueryRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
    ai_service: CommunityAIService,
) -> AiCopilotQueryResponse:
    # 1. Referral Gate Validation
    total_referrals = db.scalar(
        select(func.count(User.id)).where(User.referred_by_id == current_user.id)
    ) or 0

    if total_referrals < REQUIRED_REFERRALS_COUNT:
        ref_code = ensure_user_referral_code(db, current_user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "REFERRAL_GATE_LOCKED",
                "current": total_referrals,
                "required": REQUIRED_REFERRALS_COUNT,
                "referral_code": ref_code,
                "message": f"ميزة المساعد الذكي تشترط دعوة 5 أصدقاء لاستخدامها. قمت بدعوة ({total_referrals}/{REQUIRED_REFERRALS_COUNT}) أصدقاء حتّى الآن.",
            },
        )

    # 2. Debit 0.5 coins (50 points)
    try:
        tx_id = f"ai_copilot:{uuid4()}"
        debit_points(
            db,
            user_id=current_user.id,
            amount_points=AI_COPILOT_COST_POINTS,
            transaction_id=tx_id,
            entry_type="ai_copilot_query",
            details={"ticker": body.ticker, "question": body.question},
        )
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رصيد العملات غير كافٍ لاستخدام المساعد الذكي (التكلفة 0.5 عملة)",
        ) from exc

    # 3. Process query via AI service with community prompt strategy
    prompt = (
        f"أنت مساعد الذكاء الاصطناعي لسوق الأسهم في تطبيق سهمي كسبان.\n"
        f"سؤال المستخدم: {body.question}\n"
        f"{f'السهم المطلوب: {body.ticker}' if body.ticker else ''}\n\n"
        f"تعليمات الإجابة:\n"
        f"1. قدم تحليلاً فكلياً وتقنياً دقيقاً بأسلوب حواري مبسط.\n"
        f"2. اختم إجابتك دائماً بدعوة غير مباشرة تشجع المستخدم على نشر توقع ومناقشة في المجتمع (مثال: 'ما هو انطباعك أنت لأسعار الجلسة القادمة؟ شارك توقعك الآن في المجتمع وادعم المتداولين!')."
    )

    try:
        raw_answer = ai_service.generate_market_insight(
            ticker=body.ticker or "COMI",
            technical_data={"question": body.question, "prompt": prompt},
        )
        answer = raw_answer if isinstance(raw_answer, str) else str(raw_answer)
    except Exception:
        answer = (
            "وفقاً للبيانات الفنية الراهنة لسوق الأسهم، يُفضل متابعة مستويات السيولة ونقاط الدعم والتحول الهامة للاتجاه قبل اتخاذ القرار الاستثماري.\n\n"
            "ما هو انطباعك أنت لاتجاه السهم في الجلسة القادمة؟ شارك توقعك الآن في مجتمع المتداولين وادعم رفاقك!"
        )

    db.commit()

    return AiCopilotQueryResponse(
        answer=answer,
        ticker=body.ticker,
        coins_deducted=0.5,
    )
