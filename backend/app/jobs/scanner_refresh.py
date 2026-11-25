from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime

from app.core.config import Environment, get_settings
from app.db.session import SessionLocal
from app.market_calendar import EGXTradingCalendar
from app.market_data.provider import get_market_data_provider
from app.services.scanner import refresh_scanner_snapshot

logger = logging.getLogger(__name__)

SCANNER_KINDS: tuple[str, ...] = ("technical", "fibonacci")


def _trading_session_now() -> bool:
    calendar = EGXTradingCalendar.from_settings()
    local = datetime.now(UTC).astimezone(calendar.timezone)
    return calendar.is_trading_session(local.date())


async def run_scanner_refresh() -> dict[str, object]:
    """Refresh the technical and fibonacci scanner kinds.

    The job is idempotent (snapshots are replaced per symbol), respects the
    ``scanner_refresh_*`` settings and only runs on EGX trading days.
    """
    settings = get_settings()
    if settings.app_env is Environment.TEST:
        return {"status": "skipped", "reason": "test_environment", "count": 0}
    if not settings.scanner_refresh_enabled:
        return {"status": "skipped", "reason": "disabled", "count": 0}
    if not _trading_session_now():
        return {"status": "skipped", "reason": "non_trading_session", "count": 0}

    provider = get_market_data_provider()
    counts: dict[str, int] = {}
    failed_kinds: list[str] = []
    total = 0
    with SessionLocal() as db:
        for kind in SCANNER_KINDS:
            try:
                result = await refresh_scanner_snapshot(db, provider, kind=kind)
            except Exception:
                db.rollback()
                failed_kinds.append(kind)
                logger.exception("Scanner refresh failed for kind=%s", kind)
                continue
            count = int(result.get("count", 0))
            counts[kind] = count
            total += count

    payload: dict[str, object] = {
        "status": "completed",
        "count": total,
        "kinds": counts,
        "failed_kinds": failed_kinds,
        "as_of": datetime.now(UTC).isoformat(),
    }
    logger.info("Scanner refresh result: %s", payload)
    return payload


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(asyncio.run(run_scanner_refresh()), ensure_ascii=False))


if __name__ == "__main__":
    main()
