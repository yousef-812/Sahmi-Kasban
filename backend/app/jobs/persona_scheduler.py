from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.db.session import SessionLocal
from app.services.ai_personas import run_ai_persona_discussions
from app.services.operations_settings import get_bool_setting

logger = logging.getLogger(__name__)


async def trigger_persona_discussions_job(moment: datetime | None = None) -> dict[str, Any]:
    with SessionLocal() as db:
        if not get_bool_setting(db, "ai_personas_enabled"):
            logger.info("AI personas discussions job is disabled via setting")
            return {"status": "disabled", "created_count": 0}

        try:
            result = await run_ai_persona_discussions(db, moment=moment)
            logger.info("AI personas job execution result: %s", result)
            return result
        except Exception as exc:
            logger.exception("AI personas job execution failed: %s", exc)
            return {"status": "failed", "error": str(exc), "created_count": 0}
