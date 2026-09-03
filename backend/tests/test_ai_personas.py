from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.models import AIPersonaLog, Discussion
from app.services.ai_personas import (
    PERSONA_SPECS,
    ensure_persona_users,
    run_ai_persona_discussions,
)


def test_ensure_persona_users_creates_all_five_users(db_session):
    users = ensure_persona_users(db_session)

    assert len(users) == 5
    for spec in PERSONA_SPECS:
        assert spec.code in users
        user = users[spec.code]
        assert user.display_name == spec.display_name
        assert user.avatar_key == spec.avatar_key
        assert user.status == "active"
        assert user.email_verified is True


@pytest.mark.anyio
async def test_run_ai_persona_discussions_creates_discussions_idempotently(db_session):
    fixed_moment = datetime(2026, 9, 3, 16, 0, tzinfo=UTC)  # Thursday 16:00 UTC (19:00 Cairo, after market)

    with patch("app.services.ai_personas.SahmiAIService") as mock_ai_cls:
        mock_ai_instance = AsyncMock()
        mock_ai_instance.generate_community_persona_post.return_value = {
            "title": "تحليل السهم اليوم بالعامية",
            "content": "شايف إن السهم دا ممتاز وممكن يعمل صعود الفترة الجاية.",
            "direction": "up",
        }
        mock_ai_cls.return_value = mock_ai_instance

        res1 = await run_ai_persona_discussions(db_session, moment=fixed_moment)

        assert res1["status"] == "completed"
        assert res1["created_count"] == 5

        # Check discussions created in DB
        discussions = db_session.scalars(select(Discussion)).all()
        assert len(discussions) == 5

        for disc in discussions:
            assert disc.status == "published"
            assert disc.period_type == "next_session"

        # Check logs created in DB
        logs = db_session.scalars(select(AIPersonaLog)).all()
        assert len(logs) == 5

        # Running again for the same target session should be idempotent
        res2 = await run_ai_persona_discussions(db_session, moment=fixed_moment)
        assert res2["status"] == "already_completed"
        assert res2["created_count"] == 0
