from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Discussion, PredictionVerification, User, UserFollow
from app.schemas.community import UserPublicProfileResponse


def toggle_user_follow(
    db: Session,
    *,
    follower_id: UUID,
    following_id: UUID,
) -> tuple[bool, int]:
    """Toggles follow status between follower and target user.

    Returns (is_following, total_followers_count).
    """
    if follower_id == following_id:
        raise ValueError("Cannot follow yourself")

    target_user = db.scalar(select(User).where(User.id == following_id, User.deleted_at.is_(None)))
    if not target_user:
        raise KeyError("Target user not found")

    existing = db.scalar(
        select(UserFollow).where(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id,
        )
    )

    if existing:
        db.delete(existing)
        db.commit()
        is_following = False
    else:
        new_follow = UserFollow(follower_id=follower_id, following_id=following_id)
        db.add(new_follow)
        db.commit()
        is_following = True

    followers_count = db.scalar(
        select(func.count(UserFollow.id)).where(UserFollow.following_id == following_id)
    ) or 0

    return is_following, followers_count


def get_user_follow_stats(
    db: Session,
    *,
    user_id: UUID,
    current_user_id: UUID | None = None,
) -> tuple[int, int, bool]:
    """Returns (followers_count, following_count, is_following)."""
    followers_count = db.scalar(
        select(func.count(UserFollow.id)).where(UserFollow.following_id == user_id)
    ) or 0

    following_count = db.scalar(
        select(func.count(UserFollow.id)).where(UserFollow.follower_id == user_id)
    ) or 0

    is_following = False
    if current_user_id and current_user_id != user_id:
        existing = db.scalar(
            select(UserFollow.id).where(
                UserFollow.follower_id == current_user_id,
                UserFollow.following_id == user_id,
            )
        )
        is_following = existing is not None

    return followers_count, following_count, is_following


def get_author_prediction_stats(db: Session, *, author_id: UUID) -> tuple[int, float]:
    """Returns (predictions_count, success_rate_percent)."""
    predictions_count = db.scalar(
        select(func.count(Discussion.id)).where(
            Discussion.user_id == author_id,
            Discussion.status == "published",
        )
    ) or 0

    row = db.execute(
        select(
            func.count(PredictionVerification.id),
            func.count(PredictionVerification.id).filter(PredictionVerification.score_bp >= 4000),
        )
        .join(Discussion, Discussion.id == PredictionVerification.discussion_id)
        .where(Discussion.user_id == author_id)
    ).one()

    verified_count = int(row[0] or 0)
    accepted_count = int(row[1] or 0)

    if verified_count > 0:
        success_rate = round((accepted_count / verified_count) * 100.0, 1)
    else:
        success_rate = 0.0

    return predictions_count, success_rate


def check_and_update_analyst_tipping_unlock(db: Session, *, user_id: UUID) -> bool:
    """Checks analyst eligibility for receiving coin tips (>20 posts & >70% success rate).

    Once unlocked, tipping_unlocked remains True permanently.
    """
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        return False

    if user.tipping_unlocked:
        return True

    predictions_count, success_rate = get_author_prediction_stats(db, author_id=user_id)

    if predictions_count > 20 and success_rate > 70.0:
        user.tipping_unlocked = True
        db.add(user)
        db.commit()
        return True

    return False


def get_public_user_profile(
    db: Session,
    *,
    target_user_id: UUID,
    current_user_id: UUID | None = None,
) -> UserPublicProfileResponse:
    """Aggregates public user profile data including stats and tipping eligibility."""
    user = db.scalar(
        select(User).where(
            User.id == target_user_id,
            User.deleted_at.is_(None),
        )
    )
    if not user:
        raise KeyError("User not found")

    # Check unlock status update
    check_and_update_analyst_tipping_unlock(db, user_id=target_user_id)

    followers_count, following_count, is_following = get_user_follow_stats(
        db, user_id=target_user_id, current_user_id=current_user_id
    )

    predictions_count, success_rate = get_author_prediction_stats(db, author_id=target_user_id)

    can_receive_tips = user.tipping_unlocked and user.tipping_enabled

    can_send_tip = False
    if current_user_id and current_user_id != target_user_id:
        tipper_discussions = db.scalar(
            select(func.count(Discussion.id)).where(
                Discussion.user_id == current_user_id,
                Discussion.status == "published",
            )
        ) or 0

        can_send_tip = is_following and tipper_discussions >= 10 and can_receive_tips

    return UserPublicProfileResponse(
        user_id=user.id,
        display_name=user.display_name,
        avatar_key=user.avatar_key,
        followers_count=followers_count,
        following_count=following_count,
        predictions_count=predictions_count,
        success_rate=success_rate,
        is_following=is_following,
        tipping_unlocked=user.tipping_unlocked,
        tipping_enabled=user.tipping_enabled,
        can_receive_tips=can_receive_tips,
        can_send_tip=can_send_tip,
    )


def send_coin_tip(
    db: Session,
    *,
    sender_id: UUID,
    receiver_id: UUID,
    amount_coins: int,
) -> dict:
    """Executes a coin gift transfer from sender to analyst receiver.

    Validates all eligibility rules before deducting and crediting wallet balances.
    """
    if amount_coins <= 0:
        raise ValueError("عدد العملات يجب أن يكون أكبر من 0")

    if sender_id == receiver_id:
        raise ValueError("لا يمكنك إهداء عملات لنفسك")

    profile = get_public_user_profile(
        db, target_user_id=receiver_id, current_user_id=sender_id
    )

    if not profile.is_following:
        raise ValueError("يجب متابعة المحلل أولاً لإمكانية إهداء العملات.")

    if not profile.can_receive_tips:
        raise ValueError("المحلل لم يفعل استقبال هدايا العملات في حسابه بعد.")

    tipper_discussions = db.scalar(
        select(func.count(Discussion.id)).where(
            Discussion.user_id == sender_id,
            Discussion.status == "published",
        )
    ) or 0

    if tipper_discussions < 10:
        raise ValueError("يجب أن يكون لديك 10 مناقشات منشورين على الأقل لإهداء العملات.")

    amount_points = amount_coins * POINTS_PER_COIN
    tx_sender = f"tip:sent:{uuid4()}"
    tx_receiver = f"tip:recv:{uuid4()}"

    # Debit sender
    debit_points(
        db,
        user_id=sender_id,
        amount_points=amount_points,
        transaction_id=tx_sender,
        entry_type="coin_tip_sent",
        reference_type="user",
        reference_id=str(receiver_id),
        details={"amount_coins": amount_coins, "receiver_id": str(receiver_id)},
    )

    # Credit receiver
    credit_points(
        db,
        user_id=receiver_id,
        amount_points=amount_points,
        transaction_id=tx_receiver,
        entry_type="coin_tip_received",
        reference_type="user",
        reference_id=str(sender_id),
        details={"amount_coins": amount_coins, "sender_id": str(sender_id)},
    )

    # Log tip history
    tip_log = CoinTipHistory(
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount_coins=amount_coins,
    )
    db.add(tip_log)
    db.commit()

    return {
        "success": True,
        "amount_coins": amount_coins,
        "receiver_id": str(receiver_id),
    }


def update_analyst_tipping_settings(
    db: Session,
    *,
    user_id: UUID,
    tipping_enabled: bool,
) -> bool:
    """Updates the analyst's tipping preference toggle."""
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise KeyError("المستخدم غير موجود")

    # Check unlock condition
    unlocked = check_and_update_analyst_tipping_unlock(db, user_id=user_id)
    if not unlocked and not user.tipping_unlocked:
        raise ValueError(
            "لم تستوفِ بعد شروط فتح ميزة استقبال العملات (20 توقع بنسبة نجاح تتعدى 70%)."
        )

    user.tipping_enabled = tipping_enabled
    db.add(user)
    db.commit()
    return user.tipping_enabled

