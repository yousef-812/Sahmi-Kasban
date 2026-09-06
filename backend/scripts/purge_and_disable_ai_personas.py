from __future__ import annotations

import logging
from sqlalchemy import bindparam, text
from app.db.session import SessionLocal
from app.services.ai_personas import PERSONA_SPECS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def purge_and_disable_ai_personas() -> None:
    with SessionLocal() as db:
        # 1. Update/insert operational setting in DB
        db.execute(
            text("""
                INSERT INTO app_settings (key, category, value, description, created_at, updated_at)
                VALUES ('ai_personas_enabled', 'automation', 'false', 'السماح بتشغيل الشخصيات الخمسة لإنشاء مناقشات آلية في المجتمع.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value = 'false', updated_at = CURRENT_TIMESTAMP
            """)
        )
        logger.info("Operational setting 'ai_personas_enabled' set to False in DB.")

        # 2. Get persona user IDs
        emails = [spec.email for spec in PERSONA_SPECS]
        stmt_users = text("SELECT id FROM users WHERE email IN :emails OR email LIKE '%@sahmikasban.internal'").bindparams(
            bindparam("emails", expanding=True)
        )
        user_rows = db.execute(stmt_users, {"emails": emails}).fetchall()
        user_ids = [row[0] for row in user_rows]
        logger.info("Found %d persona user accounts.", len(user_ids))

        # 3. Delete AIPersonaLog records if table exists
        try:
            db.execute(text("DELETE FROM ai_persona_logs"))
            logger.info("Cleared ai_persona_logs table.")
        except Exception as e:
            logger.warning("Could not delete ai_persona_logs: %s", e)

        # 4. Delete discussions created by persona users
        if user_ids:
            stmt_del_ver = text("DELETE FROM prediction_verifications WHERE discussion_id IN (SELECT id FROM discussions WHERE user_id IN :user_ids)").bindparams(
                bindparam("user_ids", expanding=True)
            )
            db.execute(stmt_del_ver, {"user_ids": user_ids})

            stmt_del_disc = text("DELETE FROM discussions WHERE user_id IN :user_ids").bindparams(
                bindparam("user_ids", expanding=True)
            )
            db.execute(stmt_del_disc, {"user_ids": user_ids})
            logger.info("Deleted discussions created by persona users.")

            # Disable user accounts
            stmt_dis_user = text("UPDATE users SET status = 'disabled' WHERE id IN :user_ids").bindparams(
                bindparam("user_ids", expanding=True)
            )
            db.execute(stmt_dis_user, {"user_ids": user_ids})
            logger.info("Disabled persona user accounts.")

        db.commit()
        logger.info("Successfully purged all AI persona discussions and disabled persona features.")


if __name__ == "__main__":
    purge_and_disable_ai_personas()
