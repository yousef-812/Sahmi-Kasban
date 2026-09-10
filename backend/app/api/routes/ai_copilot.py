from __future__ import annotations

import logging
import traceback
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sahmi_kasban.ai import SahmiAIService
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.admin import is_admin_email
from app.market_data.provider import get_market_data_provider
from app.market_data.quotes import fetch_single_quote
from app.models import AiFailureLog, User
from app.services.community_ai import get_community_ai_service
from app.services.referral import ensure_user_referral_code
from app.services.wallet import InsufficientBalanceError, debit_points, get_wallet_account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-copilot", tags=["ai_copilot"])
CommunityAIService = Annotated[SahmiAIService, Depends(get_community_ai_service)]

AI_COPILOT_COST_POINTS = 50  # 0.5 coins
REQUIRED_REFERRALS_COUNT = 5


class ChatMessageHistoryItem(BaseModel):
    is_user: bool
    text: str


class AiCopilotQueryRequest(BaseModel):
    ticker: str | None = Field(default=None, max_length=24)
    question: str = Field(min_length=3, max_length=1000)
    history: list[ChatMessageHistoryItem] | None = None


class AiCopilotQueryResponse(BaseModel):
    answer: str
    ticker: str | None
    coins_deducted: float = 0.5


def _num(value: object, default: float = 0.0) -> float:
    try:
        result = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return result if result == result else default


def _build_history_context(candles: list[dict]) -> str:
    """Compact historical context (last sessions + trend stats) for the AI prompt."""
    rows: list[tuple[str, float, float, float, float]] = []
    for candle in candles:
        close = _num(candle.get("close"))
        if close <= 0:
            continue
        stamp = str(candle.get("timestamp") or "")[:10]
        rows.append(
            (
                stamp,
                _num(candle.get("open"), close),
                _num(candle.get("high"), close),
                _num(candle.get("low"), close),
                close,
            )
        )
    if len(rows) < 5:
        return ""
    closes = [r[4] for r in rows]
    last = closes[-1]
    first_open = rows[0][1]

    lines = ["📊 البيانات التاريخية للسهم (آخر الجلسات — الأحدث أخيراً):"]
    for stamp, o, _h, _l, c in rows[-10:]:
        day_change = ((c - o) / o * 100.0) if o > 0 else 0.0
        lines.append(f"- {stamp}: إغلاق {c:.2f} ({day_change:+.2f}%)")

    window = closes[-20:]
    hi, lo = max(window), min(window)
    month_change = ((last - first_open) / first_open * 100.0) if first_open > 0 else 0.0
    sma5 = sum(closes[-5:]) / min(5, len(closes))
    sma20 = sum(window) / len(window)
    pos = ((last - lo) / (hi - lo) * 100.0) if hi > lo else 50.0
    trend = (
        "صاعد (فوق متوسط 5 و20)"
        if last > sma5 >= sma20
        else "هابط (تحت متوسط 5 و20)"
        if last < sma5 <= sma20
        else "عرضي/مختلط"
    )
    lines.append(
        f"الخلاصة: تغير ~شهر {month_change:+.2f}% | أعلى {hi:.2f} وأدنى {lo:.2f} "
        f"(20 جلسة) | السعر عند {pos:.0f}% من المدى | متوسط 5 = {sma5:.2f} "
        f"| متوسط 20 = {sma20:.2f} | الاتجاه: {trend}"
    )
    return "\n".join(lines) + "\n\n"


@router.post("/query", response_model=AiCopilotQueryResponse)
async def query_ai_copilot(
    body: AiCopilotQueryRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
    ai_service: CommunityAIService,
) -> AiCopilotQueryResponse:
    cairo_now = datetime.now(UTC)
    is_admin = is_admin_email(current_user.email)

    # 1. Active Cooldown Check (1 Hour Lock after failure) - Bypassed for admin
    if not is_admin and current_user.ai_cooldown_until:
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

    # 2. Referral Gate Validation - Bypassed for admin
    if not is_admin:
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

    # 3. Check Wallet Balance before calling AI - Bypassed for admin
    if not is_admin:
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

    # 4. Fetch live market quote for accurate real-time stock price
    market_context = ""
    history_context = ""
    quote_price_strict = ""
    company_name_strict = ""
    if body.ticker:
        quote = await fetch_single_quote(db, body.ticker)
        if quote:
            change_str = f"{quote.change_percent:+.2f}%" if quote.change_percent is not None else "غير متوفر"
            quote_price_strict = f"{quote.current_price}" if quote.current_price is not None else ""
            company_name_strict = quote.description or quote.ticker
            market_context = (
                f"🚨 بيانات رسمية مؤكدة ومحدثة الآن لسهم ({quote.ticker} — {quote.description}):\n"
                f"- السعر الحالي اللحظي والمعتمد: {quote.current_price or 'غير متوفر'} جنيه\n"
                f"- التغير اليومي: {change_str}\n"
                f"- سعر الفتح: {quote.open_price or 'غير متوفر'} جنيه\n"
                f"- أعلى سعر للجلسة: {quote.session_high or 'غير متوفر'} جنيه\n"
                f"- أدنى سعر للجلسة: {quote.session_low or 'غير متوفر'} جنيه\n"
                f"- حجم التداول: {quote.volume or 'غير متوفر'}\n"
                f"- القطاع: {quote.sector or 'غير متوفر'}\n\n"
            )
        # 4b. Historical candles so the AI can discuss trend/supports.
        # Failure here must never block the query (quote-only fallback).
        try:
            provider = get_market_data_provider()
            series = await provider.get_history(
                body.ticker.strip().upper(), period="1mo", interval="1d"
            )
            history_context = _build_history_context([dict(c) for c in series.candles])
        except Exception:
            logger.warning("AI copilot history fetch failed for %s", body.ticker)

    # 5. Build prompt with conversation memory and live market quote
    history_str = ""
    if body.history:
        history_items = []
        for item in body.history[-10:]:
            role = "المستخدم" if item.is_user else "المساعد الذكي"
            clean_text = item.text.strip()
            if clean_text:
                history_items.append(f"{role}: {clean_text}")
        if history_items:
            history_str = "سياق المحادثة السابقة بينك وبين المستخدم:\n" + "\n".join(history_items) + "\n\n"

    prompt = (
        f"أنت مساعد الذكاء الاصطناعي لسوق الأسهم في تطبيق سهمي كسبان.\n"
        f"{market_context}"
        f"{history_context}"
        f"{history_str}"
        f"سؤال المستخدم الحالي: {body.question}\n"
        f"{f'السهم المطلوب: {body.ticker}' if body.ticker else ''}\n\n"
        f"تعليمات الإجابة الصارمة:\n"
        f"1. تنبيه مؤكد: سعر سهم {body.ticker or ''} ({company_name_strict}) الحالي والمعتمد هو بالضبط ({quote_price_strict} جنيه). يمنع منعاً باتاً تغيير السعر أو اختراع اسم شركة أخرى غير {company_name_strict}!\n"
        f"2. اعتمد حتماً ورسمياً على السعر الحالي ({quote_price_strict} جنيه) كإغلاق ومرجع أساسي عند تحديد الدعم والمقاومة، ولا تذكر أي أسعار قديمة أو افتراضية مخالفة.\n"
        f"3. قدم تحليلاً مالياً وتقنياً دقيقاً بأسلوب حواري مبسط وشامل.\n"
        f"4. اختم إجابتك دائماً بدعوة غير مباشرة تشجع المستخدم على نشر توقع ومناقشة في المجتمع (مثال: 'ما هو انطباعك أنت لأسعار الجلسة القادمة؟ شارك توقعك الآن في المجتمع وادعم المتداولين!').\n"
        f"5. عند الحديث عن الاتجاه أو الدعوم والمقاومات استخدم البيانات التاريخية المذكورة أعلاه فقط (الجلسات الأخيرة والمتوسطات)، ولا تخترع قمماً أو قيعاناً غير مذكورة.\n"
    )

    try:
        raw_answer = await ai_service.generate_market_insight(
            ticker=body.ticker or "COMI",
            technical_data={"question": body.question, "prompt": prompt},
        )
        answer = raw_answer if isinstance(raw_answer, str) else str(raw_answer)

        coins_deducted = 0.0
        if not is_admin:
            # Debit 0.5 coins (50 points) ONLY FOR REGULAR USERS AFTER SUCCESSFUL RESPONSE!
            tx_id = f"ai_copilot:{uuid4()}"
            debit_points(
                db,
                user_id=current_user.id,
                amount_points=AI_COPILOT_COST_POINTS,
                transaction_id=tx_id,
                entry_type="ai_copilot_query",
                details={"ticker": body.ticker, "question": body.question},
            )
            coins_deducted = 0.5
            db.commit()

        return AiCopilotQueryResponse(
            answer=answer,
            ticker=body.ticker,
            coins_deducted=coins_deducted,
        )
    except Exception as exc:
        db.rollback()
        # Log failure reason to Admin table and apply 1-hour cooldown ONLY to regular users
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
        if not is_admin:
            current_user.ai_cooldown_until = datetime.now(UTC) + timedelta(hours=1)
        db.commit()

        msg = (
            "تعذرت معالجة استفسارك بواسطة المساعد الذكي. لم يتم خصم أي عملات."
            if is_admin
            else "تعذرت معالجة استفسارك بواسطة المساعد الذكي. لم يتم خصم أي عملات، وتم إيقاف دردشة الـ AI بحسابك مؤقتاً لمدة 1 ساعة."
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error_code": "AI_SERVICE_FAILURE",
                "message": msg,
            },
        ) from exc
