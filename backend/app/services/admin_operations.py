from __future__ import annotations

import time
from datetime import UTC, datetime

from sahmi_kasban.ai import AIProviderError, SahmiAIService
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.market_data.types import MarketDataProvider
from app.models import (
    CommunityAdminEvent,
    Discussion,
    DiscussionAppeal,
    DiscussionReport,
    Notification,
    PredictionVerification,
    ServiceHealthEvent,
    Subscription,
    User,
    WalletAccount,
)


def get_admin_overview(db: Session, *, moment: datetime | None = None) -> dict:
    current = moment or datetime.now(UTC)
    today_start = current.replace(hour=0, minute=0, second=0, microsecond=0)

    def count(model, *filters) -> int:
        return int(db.scalar(select(func.count(model.id)).where(*filters)) or 0)

    return {
        "users_total": count(User),
        "users_active": count(User, User.status == "active"),
        "users_suspended": count(User, User.status == "suspended"),
        "discussions_pending": count(
            Discussion, Discussion.status == "pending_review"
        ),
        "discussions_published": count(
            Discussion, Discussion.status == "published"
        ),
        "discussions_hidden": count(Discussion, Discussion.status == "hidden"),
        "open_reports": count(DiscussionReport, DiscussionReport.status == "open"),
        "open_appeals": count(DiscussionAppeal, DiscussionAppeal.status == "open"),
        "verified_predictions": count(PredictionVerification),
        "wallet_points_total": int(
            db.scalar(select(func.coalesce(func.sum(WalletAccount.balance_points), 0)))
            or 0
        ),
        "notifications_today": count(Notification, Notification.sent_at >= today_start),
        "unread_notifications": count(Notification, Notification.read_at.is_(None)),
    }


def list_admin_users(
    db: Session,
    *,
    query_text: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    wallet_balance = (
        select(WalletAccount.balance_points)
        .where(WalletAccount.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    plan_code = (
        select(Subscription.plan_code)
        .where(
            Subscription.user_id == User.id,
            Subscription.status == "active",
        )
        .order_by(Subscription.started_at.desc())
        .limit(1)
        .correlate(User)
        .scalar_subquery()
    )
    discussions_count = (
        select(func.count(Discussion.id))
        .where(Discussion.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    filters = []
    cleaned = (query_text or "").strip()
    if cleaned:
        like = f"%{cleaned}%"
        filters.append(or_(User.email.ilike(like), User.display_name.ilike(like)))
    if status:
        filters.append(User.status == status)
    total = int(db.scalar(select(func.count(User.id)).where(*filters)) or 0)
    rows = db.execute(
        select(
            User,
            wallet_balance.label("balance_points"),
            plan_code.label("plan_code"),
            discussions_count.label("discussions_count"),
        )
        .where(*filters)
        .order_by(User.created_at.desc(), User.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [
        {
            "id": row[0].id,
            "email": row[0].email,
            "display_name": row[0].display_name,
            "status": row[0].status,
            "plan_code": row[2] or "free",
            "balance_points": int(row[1] or 0),
            "discussions_count": int(row[3] or 0),
            "created_at": row[0].created_at,
        }
        for row in rows
    ], total


def list_admin_audit_events(
    db: Session,
    *,
    action: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[CommunityAdminEvent], int]:
    filters = []
    if action:
        filters.append(CommunityAdminEvent.action == action)
    total = int(
        db.scalar(select(func.count(CommunityAdminEvent.id)).where(*filters)) or 0
    )
    items = db.scalars(
        select(CommunityAdminEvent)
        .where(*filters)
        .order_by(
            CommunityAdminEvent.created_at.desc(),
            CommunityAdminEvent.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()
    return list(items), total


def record_service_health(
    db: Session,
    *,
    component: str,
    provider: str,
    status: str,
    latency_ms: int | None,
    details: dict,
    moment: datetime | None = None,
) -> ServiceHealthEvent:
    event = ServiceHealthEvent(
        component=component,
        provider=provider,
        status=status,
        latency_ms=latency_ms,
        details=details,
        observed_at=moment or datetime.now(UTC),
    )
    db.add(event)
    db.flush()
    return event


def list_latest_service_health(db: Session) -> list[ServiceHealthEvent]:
    components = db.scalars(select(ServiceHealthEvent.component).distinct()).all()
    result: list[ServiceHealthEvent] = []
    for component in components:
        item = db.scalar(
            select(ServiceHealthEvent)
            .where(ServiceHealthEvent.component == component)
            .order_by(
                ServiceHealthEvent.observed_at.desc(),
                ServiceHealthEvent.id.desc(),
            )
            .limit(1)
        )
        if item is not None:
            result.append(item)
    return sorted(result, key=lambda item: item.component)


async def probe_service_health(
    db: Session,
    *,
    market_provider: MarketDataProvider,
    ai_service: SahmiAIService,
) -> list[ServiceHealthEvent]:
    market_start = time.perf_counter()
    try:
        series = await market_provider.get_history("COMI", period="1mo", interval="1d")
        market_status = "healthy" if series.candle_count >= 5 else "degraded"
        record_service_health(
            db,
            component="market_data",
            provider=series.provider,
            status=market_status,
            latency_ms=int((time.perf_counter() - market_start) * 1000),
            details={
                "ticker": series.ticker,
                "candle_count": series.candle_count,
                "data_as_of": series.data_as_of.isoformat(),
            },
        )
    except Exception as exc:  # provider boundary
        record_service_health(
            db,
            component="market_data",
            provider=getattr(market_provider, "name", "configured"),
            status="failed",
            latency_ms=int((time.perf_counter() - market_start) * 1000),
            details={"error": type(exc).__name__, "message": str(exc)[:300]},
        )

    ai_start = time.perf_counter()
    try:
        response = await ai_service.client.chat(
            [{"role": "user", "content": "Reply with OK only."}],
            temperature=0.0,
            max_tokens=8,
        )
        record_service_health(
            db,
            component="ai",
            provider="configured_ai",
            status="healthy" if response.strip() else "degraded",
            latency_ms=int((time.perf_counter() - ai_start) * 1000),
            details={"response_received": bool(response.strip())},
        )
    except AIProviderError as exc:
        record_service_health(
            db,
            component="ai",
            provider="configured_ai",
            status="failed",
            latency_ms=int((time.perf_counter() - ai_start) * 1000),
            details={"error": type(exc).__name__, "message": str(exc)[:300]},
        )
    db.flush()
    return list_latest_service_health(db)
