from __future__ import annotations

import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import desc, select

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.market_calendar import EGXTradingCalendar
from app.market_data.fundamental import get_egx_investment_rankings
from app.models import MarketDataSnapshot, PushDevice, User
from app.services.notifications import FCMPushSender, _decrypt_token, create_notification
from app.services.operations_settings import get_bool_setting

logger = logging.getLogger(__name__)


def _notify_investment_report_ready(db) -> int:
    if not get_bool_setting(db, "notifications_enabled"):
        return 0
    users = db.scalars(
        select(User).where(
            User.status == "active",
            User.email_verified.is_(True),
        )
    ).all()
    push_sender = FCMPushSender()
    title = "تقرير أفضل الفرص الاستثمارية والقيمة العادلة جاهز"
    body = "تم تحديث التحليل المالي الأساسي وهوامش الأمان وعوائد التوزيعات لأفضل الفرص الاستثمارية."
    data = {
        "report_type": "investment",
        "route": "/market/reports/investment/latest",
    }
    for user in users:
        create_notification(
            db,
            user_id=user.id,
            title=title,
            body=body,
            category="market_report",
            data=data,
        )
        devices = db.scalars(
            select(PushDevice).where(
                PushDevice.user_id == user.id,
                PushDevice.enabled.is_(True),
            )
        ).all()
        for device in devices:
            try:
                push_sender.send(
                    token=_decrypt_token(device.encrypted_token),
                    title=title,
                    body=body,
                    data=data,
                )
            except Exception:
                pass
    db.commit()
    return len(users)


async def run_investment_report_scan(moment: datetime | None = None) -> dict[str, object]:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    current = moment or datetime.now(UTC)
    local = current.astimezone(tz)
    calendar = EGXTradingCalendar.from_settings()

    source_date = local.date()
    if not calendar.is_trading_session(source_date):
        return {
            "status": "skipped",
            "reason": "non_trading_session",
            "detail": f"{source_date.isoformat()} is not an EGX trading session",
        }

    target_hour = settings.investment_scan_hour
    target_minute = settings.investment_scan_minute
    if (local.hour, local.minute) < (target_hour, target_minute):
        return {
            "status": "skipped",
            "reason": "before_scan_time",
            "detail": f"Investment scan scheduled for {target_hour:02d}:{target_minute:02d} Cairo time",
        }

    with SessionLocal() as db:
        snapshot = db.scalar(
            select(MarketDataSnapshot)
            .where(MarketDataSnapshot.ticker == "__INVESTMENT_RANKINGS__")
            .order_by(desc(MarketDataSnapshot.fetched_at))
        )
        if snapshot is not None and snapshot.fetched_at is not None:
            snap_local_date = snapshot.fetched_at.astimezone(tz).date()
            if snap_local_date == source_date:
                return {
                    "status": "already_exists",
                    "reason": "today_snapshot_present",
                    "fetched_at": snapshot.fetched_at.isoformat(),
                }

        try:
            rankings = await get_egx_investment_rankings(db, force_refresh=True)
            notif_count = _notify_investment_report_ready(db)
            return {
                "status": "created",
                "items_count": len(rankings),
                "notifications_sent": notif_count,
            }
        except Exception as exc:
            logger.exception("Scheduled investment report scan failed")
            return {
                "status": "failed",
                "error": str(exc),
            }
