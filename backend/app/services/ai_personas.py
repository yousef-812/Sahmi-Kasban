from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.ai import SahmiAIService
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.avatars import validate_avatar_key
from app.core.security import hash_password
from app.market_calendar import EGXTradingCalendar
from app.market_data.catalog import ensure_market_instrument_catalog
from app.market_data.egx_symbols import EGX_SEED_SYMBOLS
from app.market_data.provider import get_market_data_provider
from app.market_data.universe import apply_market_health_quarantine
from app.models import AIPersonaLog, Discussion, User, WalletAccount
from app.services.community import apply_moderation_decision, create_discussion

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AIPersonaSpec:
    code: str
    display_name: str
    email: str
    avatar_key: str
    traits: str
    sample_phrase: str


PERSONA_SPECS: tuple[AIPersonaSpec, ...] = (
    AIPersonaSpec(
        code="sherif_trader",
        display_name="شريف التمامي",
        email="persona_sherif@sahmikasban.internal",
        avatar_key="avatar_03",
        traits="مضارب جريء ومندفع، يركز على السيولة والزخم واختراق المقاومات. يتحدث بعامية مصادرية حماسية ومختصرة مثل: السهم فيه طلقة، السيولة داخلة بقوة.",
        sample_phrase="السيولة داخلة بقوة والسهم فيه طلقة صعود جيدة.",
    ),
    AIPersonaSpec(
        code="dr_moustafa",
        display_name="د. مصطفى حسني",
        email="persona_moustafa@sahmikasban.internal",
        avatar_key="avatar_05",
        traits="محلل قيمة محافظ ودقيق، يدرس نتائج الأعمال ومكررات الأرباح قبل أي حركة. يتحدث برزانة وأرقام مثل: مكرر أرباح ممتاز وتجميع هادي.",
        sample_phrase="مكرر الأرباح ممتاز والهيكل المالي متين للسياسة الاستثمارية.",
    ),
    AIPersonaSpec(
        code="kareem_smc",
        display_name="كريم فؤاد",
        email="persona_kareem@sahmikasban.internal",
        avatar_key="avatar_08",
        traits="خبير تحليل فني ومدرسة الـ Smart Money (SMC)، يركز على مناطق الطلب والدعم وسيولة المؤسسات والارتدادات.",
        sample_phrase="ارتداد متوقع من منطقة طلب وسيولة مؤسسات قوية.",
    ),
    AIPersonaSpec(
        code="sarah_investor",
        display_name="سارة علي",
        email="persona_sarah@sahmikasban.internal",
        avatar_key="avatar_10",
        traits="مستثمرة تتبع الاتجاهات القوية والأخبار ونتائج الأعمال ومشتريات الأجانب والمؤسسات.",
        sample_phrase="نتائج الأعمال إيجابية وتدفقات الأجانب بتسند السهم.",
    ),
    AIPersonaSpec(
        code="omar_value",
        display_name="عمر فاروق",
        email="persona_omar@sahmikasban.internal",
        avatar_key="avatar_02",
        traits="صائد الأسهم المظلومة التي هبطت بدون مبرر، يركز على الشراء الهادئ والتجميع التدريجي قبل الانطلاقة.",
        sample_phrase="السهم اتظلم في الهبوط الأخير وفرصة تجميع هادية.",
    ),
)


def ensure_persona_users(db: Session) -> dict[str, User]:
    users_by_code: dict[str, User] = {}
    dummy_password_hash = hash_password("PersonaBotPassword123!")

    for spec in PERSONA_SPECS:
        avatar_key = validate_avatar_key(spec.avatar_key)
        user = db.scalar(select(User).where(User.email == spec.email))
        if user is None:
            user = User(
                email=spec.email,
                password_hash=dummy_password_hash,
                display_name=spec.display_name,
                avatar_key=avatar_key,
                status="active",
                email_verified=True,
            )
            db.add(user)
            db.flush()
        else:
            if user.display_name != spec.display_name or user.avatar_key != avatar_key:
                user.display_name = spec.display_name
                user.avatar_key = avatar_key
                db.flush()

        users_by_code[spec.code] = user

        wallet = db.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
        if wallet is None:
            wallet = WalletAccount(user_id=user.id, balance_points=10000)
            db.add(wallet)
            db.flush()
        elif wallet.balance_points < 1000:
            wallet.balance_points = 10000
            db.flush()

    db.commit()
    return users_by_code


def _resolve_target_session_date(calendar: EGXTradingCalendar, moment: datetime) -> str:
    local_dt = moment.astimezone(calendar.timezone)
    current_date = local_dt.date()

    if calendar.is_trading_session(current_date):
        if local_dt.timetz().replace(tzinfo=None) >= calendar.scan_time:
            target_date = calendar.next_trading_session(current_date)
        else:
            target_date = current_date
    else:
        target_date = calendar.next_trading_session(current_date)

    return target_date.isoformat()


async def run_ai_persona_discussions(
    db: Session,
    *,
    moment: datetime | None = None,
) -> dict[str, Any]:
    now = moment or datetime.now(UTC)
    calendar = EGXTradingCalendar.from_settings()

    target_session_date = _resolve_target_session_date(calendar, now)
    persona_users = ensure_persona_users(db)

    existing_logs = db.scalars(
        select(AIPersonaLog).where(AIPersonaLog.target_session_date == target_session_date)
    ).all()
    completed_codes = {log.persona_code for log in existing_logs}

    remaining_specs = [spec for spec in PERSONA_SPECS if spec.code not in completed_codes]
    if not remaining_specs:
        return {
            "status": "already_completed",
            "target_session_date": target_session_date,
            "created_count": 0,
        }

    await ensure_market_instrument_catalog(db)
    universe = apply_market_health_quarantine(db)
    available_tickers = list(universe.tickers or EGX_SEED_SYMBOLS)

    used_tickers = {log.ticker for log in existing_logs}
    selectable_tickers = [t for t in available_tickers if t not in used_tickers]
    if not selectable_tickers:
        selectable_tickers = available_tickers

    ai_service = SahmiAIService()
    analyzer = SahmiKasbanAnalyzer(AnalysisConfig())
    created_count = 0

    for index, spec in enumerate(remaining_specs):
        ticker = selectable_tickers[index % len(selectable_tickers)]
        user = persona_users[spec.code]

        provider = get_market_data_provider()
        analysis_dict = {"ticker": ticker}
        try:
            series = provider.fetch_daily_series(ticker)
            if series and series.candles:
                analysis_dict = analyzer.analyze(ticker, series.candles).to_dict()
        except Exception as exc:
            logger.debug("Could not fetch market series for %s: %s", ticker, exc)

        try:
            generated = await ai_service.generate_community_persona_post(
                persona_name=spec.display_name,
                persona_traits=spec.traits,
                ticker=ticker,
                stock_analysis=analysis_dict,
            )
            title = str(generated.get("title", f"رأيي في سهم {ticker}"))[:120]
            content = str(generated.get("content", spec.sample_phrase))[:2000]
        except Exception as exc:
            logger.warning("AI generation failed for persona %s on ticker %s: %s", spec.code, ticker, exc)
            title = f"رأيي التحليلي في سهم {ticker}"
            content = f"{spec.sample_phrase} شايف حركة إيجابية متوقعة في سهم {ticker} للجلسة الجاية."

        submission_key = f"persona_{spec.code}_{target_session_date}"

        try:
            sub_res = create_discussion(
                db,
                user=user,
                submission_key=submission_key,
                ticker=ticker,
                title=title,
                content=content,
                period_type="next_session",
                moment=now,
            )
            discussion = apply_moderation_decision(
                db,
                discussion_id=sub_res.discussion.id,
                decision="accept",
                actor_type="system",
                moment=now,
            )

            log_entry = AIPersonaLog(
                persona_code=spec.code,
                user_id=user.id,
                discussion_id=discussion.id,
                ticker=ticker,
                target_session_date=target_session_date,
                details={
                    "display_name": spec.display_name,
                    "title": title,
                    "generated_by_ai": True,
                },
            )
            db.add(log_entry)
            db.commit()
            created_count += 1
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to create persona discussion for %s on %s: %s", spec.code, ticker, exc)

    return {
        "status": "completed",
        "target_session_date": target_session_date,
        "created_count": created_count,
    }
