from __future__ import annotations

import logging

from app.db.session import SessionLocal
from app.services.wallet import grant_due_weekly_points

logger = logging.getLogger(__name__)


def run_weekly_wallet_grants() -> int:
    with SessionLocal() as db:
        try:
            granted = grant_due_weekly_points(db)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Weekly wallet grant job failed")
            raise
    logger.info("Weekly wallet grant job completed; granted=%s", granted)
    return granted


if __name__ == "__main__":
    run_weekly_wallet_grants()
