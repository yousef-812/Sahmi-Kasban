from __future__ import annotations

import asyncio
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
from app.models import AiFailureLog, MarketInstrumentCatalog, User
from app.services.community_ai import get_community_ai_service
from app.services.news import extract_tickers_from_text
from app.services.referral import ensure_user_referral_code
from app.services.wallet import InsufficientBalanceError, debit_points, get_wallet_account

logger = logging.getLogger(__name__)

MAX_QUERY_TICKERS = 5

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


def _build_history_context(candles: list[dict], *, recent_n: int = 10) -> str:
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
    for stamp, o, _h, _l, c in rows[-recent_n:]:
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


def _resolve_query_tickers(db, *, explicit: str | None, question: str) -> list[str]:
    """Tickers for a copilot query: explicit field first, then symbols/names
    mentioned in the question text. Never raises."""
    ordered: list[str] = []
    if explicit and explicit.strip():
        ordered.append(explicit.strip().upper())
    try:
        known = frozenset(
            db.scalars(
                select(MarketInstrumentCatalog.ticker).where(
                    MarketInstrumentCatalog.active.is_(True)
                )
            ).all()
        )
    except Exception:
        known = frozenset()
    try:
        for ticker, _score in extract_tickers_from_text(question or "", known):
            clean = ticker.strip().upper()
            if clean and clean not in ordered:
                ordered.append(clean)
    except Exception:
        pass
    return ordered[:MAX_QUERY_TICKERS]


async def _safe_history(provider, ticker: str) -> list[dict]:
    """Daily candles for a ticker. Returns [] on any failure."""
    try:
        series = await provider.get_history(ticker, period="1mo", interval="1d")
        return [dict(c) for c in series.candles]
    except Exception:
        logger.warning("AI copilot history fetch failed for %s", ticker)
        return []


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

    # 4. Resolve tickers (explicit field + symbols mentioned in the question)
    # and fetch live quote + historical candles for each of them.
    tickers = _resolve_query_tickers(db, explicit=body.ticker, question=body.question)
    market_blocks: list[str] = []
    strict_price_lines: list[str] = []
    primary_ticker = tickers[0] if tickers else None

    if tickers:
        provider = get_market_data_provider()
        histories = await asyncio.gather(*[_safe_history(provider, t) for t in tickers])
        for index, (ticker, candles) in enumerate(zip(tickers, histories, strict=True)):
            try:
                quote = await fetch_single_quote(db, ticker)
            except Exception:
                quote = None
            if quote is None and not candles:
                continue
            name = (quote.description or ticker) if quote else ticker
            if quote:
                change_str = (
                    f"{quote.change_percent:+.2f}%"
                    if quote.change_percent is not None
                    else "غير متوفر"
                )
                if quote.current_price is not None:
                    strict_price_lines.append(
                        f"- {ticker} ({name}): {quote.current_price} جنيه"
                    )
                market_blocks.append(
                    f"🚨 بيانات رسمية مؤكدة ومحدثة الآن لسهم ({ticker} — {name}):\n"
                    f"- السعر الحالي اللحظي والمعتمد: {quote.current_price or 'غير متوفر'} جنيه\n"
                    f"- التغير اليومي: {change_str}\n"
                    f"- سعر الفتح: {quote.open_price or 'غير متوفر'} جنيه\n"
                    f"- أعلى سعر للجلسة: {quote.session_high or 'غير متوفر'} جنيه\n"
                    f"- أدنى سعر للجلسة: {quote.session_low or 'غير متوفر'} جنيه\n"
                    f"- حجم التداول: {quote.volume or 'غير متوفر'}\n"
                    f"- القطاع: {quote.sector or 'غير متوفر'}\n"
                )
            else:
                market_blocks.append(
                    f"سهم ({ticker} — {name}): لا توجد بيانات لحظية متاحة حالياً.\n"
                )
            if candles:
                market_blocks.append(
                    _build_history_context(candles, recent_n=10 if index == 0 else 5)
                )

    market_context = "\n".join(market_blocks)
    if market_context:
        market_context += "\n"

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

    analyzed_line = ""
    if tickers:
        analyzed_line = f"الأسهم التي تم جلب بياناتها لتحليلها: { '، '.join(tickers)}\n\n"
    strict_block = ""
    if strict_price_lines:
        strict_block = "الأسعار المعتمدة (ممنوع تغييرها):\n" + "\n".join(strict_price_lines) + "\n"

    prompt = (
        f"أنت مساعد الذكاء الاصطناعي لسوق الأسهم في تطبيق سهمي كسبان.\n"
        f"{market_context}"
        f"{history_str}"
        f"سؤال المستخدم الحالي: {body.question}\n"
        f"{analyzed_line}"
        f"تعليمات الإجابة الصارمة:\n"
        f"1. تنبيه مؤكد:\n{strict_block}"
        f"يمنع منعاً باتاً تغيير أي سعر أو اختراع أسعار أو شركات غير مذكورة أعلاه!\n"
        f"2. اعتمد حتماً ورسمياً على الأسعار المعتمدة أعلاه كإغلاق ومرجع أساسي عند تحديد الدعم والمقاومة لكل سهم، ولا تذكر أي أسعار قديمة أو افتراضية مخالفة.\n"
        f"3. قدم تحليلاً مالياً وتقنياً دقيقاً بأسلوب حواري مبسط وشامل. عند ذكر أكثر من سهم حلل كل سهم باختصار ثم قارن بينهم.\n"
        f"4. اختم إجابتك دائماً بدعوة غير مباشرة تشجع المستخدم على نشر توقع ومناقشة في المجتمع (مثال: 'ما هو انطباعك أنت لأسعار الجلسة القادمة؟ شارك توقعك الآن في المجتمع وادعم المتداولين!').\n"
        f"5. عند الحديث عن الاتجاه أو الدعوم والمقاومات استخدم البيانات التاريخية المذكورة أعلاه فقط (الجلسات الأخيرة والمتوسطات)، ولا تخترع قمماً أو قيعاناً غير مذكورة.\n"
        f"6. ممنوع الرد بعبارات مثل 'لا تتوفر بيانات' عن أي سهم مذكور أعلاه ببياناته — البيانات أمامك وحللها مباشرة.\n"
    )

    try:
        raw_answer = await ai_service.generate_market_insight(
            ticker=primary_ticker or "COMI",
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
