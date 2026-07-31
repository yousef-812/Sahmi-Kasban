from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import PushDevice, User
from app.services.profile import soft_delete_account


def test_soft_delete_removes_registered_push_devices(db_session: Session) -> None:
    user = User(
        email="delete-me@example.com",
        password_hash=hash_password("StrongPassword1!"),
        display_name="Delete Me",
        email_verified=True,
    )
    db_session.add(user)
    db_session.flush()
    device = PushDevice(
        user_id=user.id,
        token_hash="a" * 64,
        encrypted_token="encrypted-fixture-token",
        platform="android",
        enabled=True,
        last_seen_at=datetime.now(UTC),
    )
    db_session.add(device)
    db_session.commit()
    device_id = device.id

    soft_delete_account(db_session, user, password="StrongPassword1!")
    db_session.commit()

    assert user.status == "deleted"
    assert user.email.endswith("@deleted.invalid")
    assert db_session.get(PushDevice, device_id) is None
    assert db_session.scalar(
        select(PushDevice).where(PushDevice.user_id == user.id)
    ) is None
