import pytest
from app.models import User, WalletAccount
from app.api.routes.sector_reports import get_sector_leaderboard
from fastapi import HTTPException


def test_sector_leaderboard(db_session):
    u = User(
        email="sector_user@example.com",
        password_hash="hash",
        display_name="Sector User",
    )
    db_session.add(u)
    db_session.commit()

    w = WalletAccount(user_id=u.id, balance_points=1000)
    db_session.add(w)
    db_session.commit()

    # Invalid sector -> 404
    with pytest.raises(HTTPException) as exc:
        get_sector_leaderboard(sector_id="invalid_sector", db=db_session, current_user=u)
    assert exc.value.status_code == 404

    # Valid sector (banking)
    res = get_sector_leaderboard(sector_id="banking", db=db_session, current_user=u)
    assert res.sector_code == "banking"
    assert res.leader_ticker == "COMI"
    assert len(res.items) > 0
    assert res.coins_deducted == 2.0
