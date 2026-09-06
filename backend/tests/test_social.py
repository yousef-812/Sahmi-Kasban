import pytest
from uuid import uuid4

from app.models import User
from app.services.social import (
    get_author_prediction_stats,
    get_public_user_profile,
    get_user_follow_stats,
    toggle_user_follow,
)


def test_toggle_user_follow(db_session):
    u1 = User(
        email="user1@example.com",
        password_hash="hash",
        display_name="User One",
    )
    u2 = User(
        email="user2@example.com",
        password_hash="hash",
        display_name="User Two",
    )
    db_session.add_all([u1, u2])
    db_session.commit()

    # Self-follow error check
    with pytest.raises(ValueError, match="Cannot follow yourself"):
        toggle_user_follow(db_session, follower_id=u1.id, following_id=u1.id)

    # First follow
    is_following, followers_count = toggle_user_follow(
        db_session, follower_id=u1.id, following_id=u2.id
    )
    assert is_following is True
    assert followers_count == 1

    # Check stats
    followers, following, is_f = get_user_follow_stats(
        db_session, user_id=u2.id, current_user_id=u1.id
    )
    assert followers == 1
    assert following == 0
    assert is_f is True

    # Unfollow
    is_following_after, followers_count_after = toggle_user_follow(
        db_session, follower_id=u1.id, following_id=u2.id
    )
    assert is_following_after is False
    assert followers_count_after == 0


def test_get_public_user_profile(db_session):
    u = User(
        email="analyst@example.com",
        password_hash="hash",
        display_name="Analyst User",
    )
    db_session.add(u)
    db_session.commit()

    profile = get_public_user_profile(db_session, target_user_id=u.id)
    assert profile.user_id == u.id
    assert profile.display_name == "Analyst User"
    assert profile.followers_count == 0
    assert profile.following_count == 0
    assert profile.predictions_count == 0
    assert profile.success_rate == 0.0
    assert profile.can_receive_tips is False


def test_send_coin_tip_validation(db_session):
    from app.services.social import send_coin_tip

    u1 = User(email="tipper@example.com", password_hash="hash", display_name="Tipper")
    u2 = User(email="analyst2@example.com", password_hash="hash", display_name="Analyst 2")
    db_session.add_all([u1, u2])
    db_session.commit()

    # Should fail if not following analyst
    with pytest.raises(ValueError, match="يجب متابعة المحلل أولاً"):
        send_coin_tip(db_session, sender_id=u1.id, receiver_id=u2.id, amount_coins=5)

