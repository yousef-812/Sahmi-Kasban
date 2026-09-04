from __future__ import annotations

import logging
import random
import string
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User, WalletEntry
from app.services.wallet import POINTS_PER_COIN, credit_points

logger = logging.getLogger(__name__)

PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile"
REFERRAL_REWARD_POINTS = 1000  # Equal to 10.00 coins


def _random_code(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits.replace("0", "").replace("O", "").replace("1", "").replace(
        "I", ""
    )
    return "SK-" + "".join(random.choices(chars, k=length))


def ensure_user_referral_code(db: Session, user: User) -> str:
    """Ensure a user has a unique referral code assigned."""
    if user.referral_code:
        return user.referral_code

    for _ in range(20):
        code = _random_code()
        existing = db.scalar(select(User.id).where(User.referral_code == code))
        if existing is None:
            user.referral_code = code
            db.flush()
            return code

    # Fallback to UUID-based string if random collisions happen
    fallback_code = f"SK-{user.id.hex[:6].upper()}"
    user.referral_code = fallback_code
    db.flush()
    return fallback_code


def find_user_by_referral_code(db: Session, code: str) -> User | None:
    clean_code = code.strip().upper()
    if not clean_code:
        return None
    user = db.scalar(select(User).where(User.referral_code == clean_code))
    if user is not None:
        return user
    if not clean_code.startswith("SK-"):
        user = db.scalar(select(User).where(User.referral_code == f"SK-{clean_code}"))
        if user is not None:
            return user
    if clean_code.startswith("SK-"):
        without_prefix = clean_code[3:]
        user = db.scalar(select(User).where(User.referral_code == without_prefix))
        if user is not None:
            return user
    return None


def process_referral_rewards_on_email_verified(db: Session, user: User) -> bool:
    """Grant 10 coins (1000 points) to both referrer and referee upon email verification."""
    if not user.referred_by_id:
        return False

    referrer = db.scalar(select(User).where(User.id == user.referred_by_id))
    if referrer is None:
        return False

    # Check idempotency: make sure referrer hasn't been rewarded for this referee user ID
    existing_entry = db.scalar(
        select(WalletEntry.id).where(
            WalletEntry.user_id == referrer.id,
            WalletEntry.entry_type == "referral_reward_referrer",
            WalletEntry.reference_type == "user_referral",
            WalletEntry.reference_id == str(user.id),
        )
    )
    if existing_entry is not None:
        return False

    # 1. Reward the referrer (الداعي)
    credit_points(
        db,
        user_id=referrer.id,
        amount_points=REFERRAL_REWARD_POINTS,
        transaction_id=f"ref_referrer_{referrer.id}_{user.id}",
        entry_type="referral_reward_referrer",
        reference_type="user_referral",
        reference_id=str(user.id),
    )

    # 2. Reward the referee (المسجل الجديد)
    credit_points(
        db,
        user_id=user.id,
        amount_points=REFERRAL_REWARD_POINTS,
        transaction_id=f"ref_referee_{user.id}_{referrer.id}",
        entry_type="referral_reward_referee",
        reference_type="user_referral",
        reference_id=str(referrer.id),
    )

    logger.info(
        "Granted referral rewards (10 coins each) for referrer %s and referee %s", referrer.id, user.id
    )
    return True


def get_user_referral_stats(db: Session, user: User) -> dict[str, Any]:
    referral_code = ensure_user_referral_code(db, user)

    # Auto-reconcile any pending referral rewards for verified users
    referred_users = list(
        db.scalars(select(User).where(User.referred_by_id == user.id).order_by(User.created_at.desc())).all()
    )
    for referee in referred_users:
        if referee.email_verified:
            process_referral_rewards_on_email_verified(db, referee)
    db.flush()

    total_referrals_count = len(referred_users)

    # Calculate total earned points from referrals
    earned_points = (
        db.scalar(
            select(func.coalesce(func.sum(WalletEntry.amount_points), 0)).where(
                WalletEntry.user_id == user.id,
                WalletEntry.entry_type == "referral_reward_referrer",
            )
        )
        or 0
    )

    total_earned_points = int(earned_points)
    total_earned_coins_str = f"{total_earned_points / POINTS_PER_COIN:.2f}"

    share_text = (
        f"حمل تطبيق سهمي كسبان للتحليل الفني وسوق الأسهم المصرية!\n\n"
        f"🎁 استخدم كود الدعوة الخاص بي: {referral_code}\n"
        f"للحصول على 10 عملات مجانية (1,000 نقطة) عند إنشاء حسابك وتأكيده.\n\n"
        f"رابط التنزيل المباشر من متجر جوجل بلاي:\n{PLAY_STORE_URL}"
    )

    recent_list = []
    for referee in referred_users[:30]:
        is_verified = referee.email_verified
        recent_list.append(
            {
                "display_name": referee.display_name,
                "avatar_key": referee.avatar_key,
                "joined_at": referee.created_at.strftime("%Y-%m-%d") if referee.created_at else "",
                "registered_at": referee.created_at.isoformat() if referee.created_at else None,
                "status": "verified" if is_verified else "pending",
                "earned_points": REFERRAL_REWARD_POINTS if is_verified else 0,
                "earned_coins": "10.00" if is_verified else "0.00",
            }
        )

    return {
        "referral_code": referral_code,
        "play_store_url": PLAY_STORE_URL,
        "share_text": share_text,
        "reward_coins_per_referral": 10.0,
        "reward_points_per_referral": REFERRAL_REWARD_POINTS,
        "total_referrals_count": total_referrals_count,
        "total_referred_count": total_referrals_count,
        "total_earned_points": total_earned_points,
        "total_earned_coins": total_earned_coins_str,
        "recent_referrals": recent_list,
        "referred_users": recent_list,
    }
