"""Purge AI persona discussions and disable AI personas feature.

Revision ID: 0034_purge_and_disable_ai_personas
Revises: 0033_daily_chat_session_votes
Create Date: 2026-09-06
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0034_purge_and_disable_ai_personas"
down_revision: str | None = "0033_daily_chat_session_votes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERSONA_EMAILS = (
    "persona_sherif@sahmikasban.internal",
    "persona_moustafa@sahmikasban.internal",
    "persona_kareem@sahmikasban.internal",
    "persona_sarah@sahmikasban.internal",
    "persona_omar@sahmikasban.internal",
)


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Update or insert app_settings
    conn.execute(
        sa.text("""
            INSERT INTO app_settings (key, category, value, description, created_at, updated_at)
            VALUES ('ai_personas_enabled', 'automation', 'false', 'السماح بتشغيل الشخصيات الخمسة لإنشاء مناقشات آلية في المجتمع.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = 'false', updated_at = CURRENT_TIMESTAMP
        """)
    )

    # 2. Delete prediction_verifications linked to persona discussions
    conn.execute(
        sa.text("""
            DELETE FROM prediction_verifications 
            WHERE discussion_id IN (
                SELECT d.id FROM discussions d 
                JOIN users u ON u.id = d.user_id 
                WHERE u.email IN :emails OR u.email LIKE '%@sahmikasban.internal'
            )
        """),
        {"emails": PERSONA_EMAILS},
    )

    # 3. Delete discussions created by persona users
    conn.execute(
        sa.text("""
            DELETE FROM discussions 
            WHERE user_id IN (
                SELECT id FROM users 
                WHERE email IN :emails OR email LIKE '%@sahmikasban.internal'
            )
        """),
        {"emails": PERSONA_EMAILS},
    )

    # 4. Clear ai_persona_logs table if exists
    with sa.orm.Session(bind=conn) as session:
        try:
            session.execute(sa.text("DELETE FROM ai_persona_logs"))
            session.commit()
        except Exception:
            pass

    # 5. Disable persona user accounts
    conn.execute(
        sa.text("""
            UPDATE users SET status = 'disabled' 
            WHERE email IN :emails OR email LIKE '%@sahmikasban.internal'
        """),
        {"emails": PERSONA_EMAILS},
    )


def downgrade() -> None:
    pass
