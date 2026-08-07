import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.admin import configured_admin_emails
from app.db.session import SessionLocal
from app.models import Subscription, User, WalletAccount


def main():
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    
    # We will search for yousefftaalip@gmail.com and any other configured admin emails
    target_emails = {"yousefftaalip@gmail.com"} | set(configured_admin_emails())
    target_emails = {email.strip().casefold() for email in target_emails if email.strip()}
    
    print(f"Target admin emails to set as PRO: {target_emails}")
    
    for email in target_emails:
        user = db.scalar(select(User).where(User.email.ilike(email)))
        if not user:
            print(f"User with email '{email}' not found in the database.")
            continue
            
        print(f"Found user: {user.display_name} (ID: {user.id})")
        
        # 1. Update/Create Pro Subscription
        sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
        if sub:
            sub.plan_code = "pro"
            sub.weekly_points = 15000
            sub.ads_enabled = False
            sub.status = "active"
            sub.expires_at = None
            print(f"Updated existing subscription to PRO for user {user.display_name}")
        else:
            sub = Subscription(
                user_id=user.id,
                plan_code="pro",
                weekly_points=15000,
                ads_enabled=False,
                status="active",
                started_at=datetime.now(UTC),
                expires_at=None
            )
            db.add(sub)
            print(f"Created new PRO subscription for user {user.display_name}")
            
        # 2. Credit Wallet with points (e.g. 50,000 points = 500 coins)
        wallet = db.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
        if wallet:
            wallet.balance_points = max(wallet.balance_points, 50000)
            print(f"Updated wallet balance to {wallet.balance_points} points for user {user.display_name}")
        else:
            wallet = WalletAccount(
                user_id=user.id,
                balance_points=50000
            )
            db.add(wallet)
            print(f"Created new wallet with 50,000 points for user {user.display_name}")
            
        db.commit()
        print(f"Successfully committed changes for user {user.display_name}")
        
    db.close()

if __name__ == '__main__':
    main()
