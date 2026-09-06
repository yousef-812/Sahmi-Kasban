from __future__ import annotations

import traceback
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sahmi_kasban.ai import SahmiAIService
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import AiFailureLog, User
from app.services.community_ai import get_community_ai_service
from app.services.referral import ensure_user_referral_code
from app.services.wallet import InsufficientBalanceError, debit_points, get_wallet_account

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
    cairo_now = datetime.now(UTC)

    # 1. Active Cooldown Check (1 Hour Lock after failure)
    if current_user.ai_cooldown_until:
        cooldown_until = current_user.ai_cooldown_until
        if cooldown_until.tzinfo is None:
            cooldown_until = cooldown_until.replace(tzinfo=UTC)
        if cairo_now < cooldown_until:
            remaining_seconds = int((cooldown_until - cairo_now).total_seconds())
            remaining_mins = max(1, remaining_seconds // 60)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "AI_COOLDOWN_ACTIVE",
                    "cooldown_until": cooldown_until.isoformat(),
                    "remaining_minutes": remaining_mins,
                    "message": f"تم إيقاف المساعد الذكي بحسابك مؤقتاً لمدة 1 ساعة بسبب تعذر معالجة استفسارك السابق. متبقي {remaining_mins} دقيقة للمحاولة مجدداً.",
                },
            )
        else:
            current_user.ai_cooldown_until = None
            db.commit()

    # 2. Referral Gate Validation
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

    # 3. Check Wallet Balance before calling AI (must have at least 0.5 coins / 50 points)
    try:
        wallet = get_wallet_account(db, current_user.id)
        if wallet.balance_points < AI_COPILOT_COST_POINTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رصيد العملات غير كافٍ لاستخدام المساعد الذكي (التكلفة 0.5 عملة)",
            )
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رصيد العملات غير كافٍ لاستخدام المساعد الذكي (التكلفة 0.5 عملة)",
        ) from exc

    # 4. Process query via AI service
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

        # Debit 0.5 coins (50 points) ONLY AFTER SUCCESSFUL RESPONSE GENERATION!
        tx_id = f"ai_copilot:{uuid4()}"
        debit_points(
            db,
            user_id=current_user.id,
            amount_points=AI_COPILOT_COST_POINTS,
            transaction_id=tx_id,
            entry_type="ai_copilot_query",
            details={"ticker": body.ticker, "question": body.question},
        )
        db.commit()

        return AiCopilotQueryResponse(
            answer=answer,
            ticker=body.ticker,
            coins_deducted=0.5,
        )
    except Exception as exc:
        db.rollback()
        # Log failure reason to Admin table and apply 1-hour cooldown to user
        tb_str = traceback.format_exc()
        failure_log = AiFailureLog(
            user_id=current_user.id,
            user_name=current_user.display_name or "مستخدم",
            user_email=current_user.email,
            ticker=body.ticker,
            question=body.question,
            error_message=str(exc),
            error_traceback=tb_str,
            created_at=datetime.now(UTC),
        )
        db.add(failure_log)
        current_user.ai_cooldown_until = datetime.now(UTC) + timedelta(hours=1)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error_code": "AI_SERVICE_FAILURE",
                "message": "تعذرت معالجة استفسارك بواسطة المساعد الذكي. لم يتم خصم أي عملات، وتم إيقاف دردشة الـ AI بحسابك مؤقتاً لمدة 1 ساعة.",
            },
        ) from exc
