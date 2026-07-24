from app.db.base import Base
from app.models import Subscription, WalletEntry


def test_foundational_tables_are_registered() -> None:
    assert {
        "users",
        "wallet_entries",
        "subscriptions",
        "market_reports",
        "market_report_items",
        "stock_analyses",
        "discussions",
        "prediction_verifications",
    }.issubset(Base.metadata.tables)


def test_free_plan_default_is_three_weekly_coins() -> None:
    weekly_points_default = Subscription.__table__.c.weekly_points.default
    assert weekly_points_default is not None
    assert weekly_points_default.arg == 300


def test_wallet_transaction_id_is_unique() -> None:
    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in WalletEntry.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }
    assert ("transaction_id",) in unique_constraints
