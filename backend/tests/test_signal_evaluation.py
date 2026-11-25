from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Environment
from app.jobs import signal_evaluation
from app.models import Alert, Signal, User
from app.services.signal_lifecycle import advance_signal, open_signal


class _StubSettings:
    def __init__(
        self,
        *,
        app_env: Environment = Environment.DEVELOPMENT,
        enabled: bool = True,
        minutes: int = 5,
    ) -> None:
        self.app_env = app_env
        self.signal_evaluation_enabled = enabled
        self.signal_evaluation_minutes = minutes


def _quote(*, price: float, high: float | None = None, low: float | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        ticker="COMI",
        current_price=price,
        session_high=high,
        session_low=low,
    )


def _install(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    *,
    quote: SimpleNamespace | None = None,
    settings: _StubSettings | None = None,
    trading: bool = True,
) -> None:
    factory = sessionmaker(bind=db_session.get_bind(), autoflush=False, expire_on_commit=False)

    async def _stub_quote(_db: Session, ticker: str, *, force_refresh: bool = False):
        if quote is None:
            return None
        return SimpleNamespace(
            ticker=ticker,
            current_price=quote.current_price,
            session_high=quote.session_high,
            session_low=quote.session_low,
        )

    monkeypatch.setattr(signal_evaluation, "SessionLocal", factory)
    monkeypatch.setattr(signal_evaluation, "get_settings", lambda: settings or _StubSettings())
    monkeypatch.setattr(signal_evaluation, "_trading_session_now", lambda: trading)
    monkeypatch.setattr(signal_evaluation, "fetch_single_quote", _stub_quote)
    monkeypatch.setattr(signal_evaluation, "_last_started", None, raising=False)


def _active_user(db: Session, *, email: str, active: bool = True, verified: bool = True) -> User:
    user = User(
        email=email,
        password_hash="hashed-password",
        display_name=email.split("@")[0],
        status="active" if active else "suspended",
        email_verified=verified,
    )
    db.add(user)
    db.commit()
    return user


def _open_long(db: Session, **overrides) -> Signal:
    params = {
        "ticker": "COMI",
        "direction": "long",
        "entry": 100.0,
        "stop": 95.0,
        "targets": (105.0, 110.0, 115.0),
        "source": "manual",
    }
    params.update(overrides)
    return open_signal(db, **params)


def test_job_skips_in_test_environment() -> None:
    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "skipped"
    assert result["reason"] == "test_environment"


def test_job_skips_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        signal_evaluation,
        "get_settings",
        lambda: _StubSettings(enabled=False),
    )

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "skipped"
    assert result["reason"] == "disabled"


def test_job_skips_when_throttled(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch, db_session)
    monkeypatch.setattr(signal_evaluation, "_last_started", time.monotonic())

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "skipped"
    assert result["reason"] == "throttled"


def test_job_skips_outside_trading_session(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch, db_session, trading=False)

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "skipped"
    assert result["reason"] == "non_trading_session"


def test_entry_reached_creates_alert_for_owner(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _active_user(db_session, email="signal-owner@example.com")
    signal = _open_long(db_session, user_id=user.id)
    _install(
        monkeypatch,
        db_session,
        quote=_quote(price=101.0, high=102.0, low=99.0),
    )

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "completed"
    assert result["evaluated"] == 1
    assert result["transitions"] == 1
    assert result["alerts"] == 1

    db_session.expire_all()
    refreshed = db_session.scalar(select(Signal).where(Signal.id == signal.id))
    assert refreshed is not None
    assert refreshed.state == "buy"

    alerts = list(db_session.scalars(select(Alert).where(Alert.user_id == user.id)))
    assert len(alerts) == 1
    assert alerts[0].type == "signal_transition"
    assert alerts[0].ref_id == signal.id
    assert alerts[0].is_read is False


def test_shared_signal_alerts_every_active_verified_user(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _active_user(db_session, email="shared-one@example.com")
    second = _active_user(db_session, email="shared-two@example.com")
    _active_user(db_session, email="shared-pending@example.com", verified=False)
    signal = _open_long(db_session, source="daily_top10")
    _install(
        monkeypatch,
        db_session,
        quote=_quote(price=101.0, high=102.0, low=99.0),
    )

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "completed"
    assert result["transitions"] == 1
    assert result["alerts"] == 2

    db_session.expire_all()
    alerts = list(db_session.scalars(select(Alert).where(Alert.ref_id == signal.id)))
    assert {alert.user_id for alert in alerts} == {first.id, second.id}


def test_stop_hit_closes_signal_and_emits_two_alerts(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _active_user(db_session, email="stop-owner@example.com")
    signal = _open_long(db_session, user_id=user.id)
    advance_signal(db_session, signal, high=101.0, low=99.0, close=100.5)
    assert signal.state == "buy"
    _install(
        monkeypatch,
        db_session,
        quote=_quote(price=96.0, high=100.0, low=94.0),
    )

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "completed"
    assert result["transitions"] == 1
    assert result["closed"] == 1
    assert result["alerts"] == 2

    db_session.expire_all()
    refreshed = db_session.scalar(select(Signal).where(Signal.id == signal.id))
    assert refreshed is not None
    assert refreshed.state == "closed"
    assert refreshed.pnl_pct is not None
    assert float(refreshed.pnl_pct) == -5.0

    events = [event.event for event in refreshed.events]
    assert events == ["opened", "buy", "tsl", "closed"]
    alerts = list(db_session.scalars(select(Alert).where(Alert.user_id == user.id)))
    assert len(alerts) == 2


def test_evaluation_is_idempotent_across_runs(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _active_user(db_session, email="idempotent@example.com")
    signal = _open_long(db_session, user_id=user.id)
    _install(
        monkeypatch,
        db_session,
        quote=_quote(price=101.0, high=102.0, low=99.0),
    )

    first = asyncio.run(signal_evaluation.run_signal_evaluation())
    monkeypatch.setattr(signal_evaluation, "_last_started", None, raising=False)
    second = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert first["transitions"] == 1
    assert first["alerts"] == 1
    assert second["transitions"] == 0
    assert second["alerts"] == 0
    assert second["evaluated"] == 1

    db_session.expire_all()
    alerts = list(db_session.scalars(select(Alert).where(Alert.ref_id == signal.id)))
    assert len(alerts) == 1


def test_missing_quote_leaves_signal_untouched(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _active_user(db_session, email="no-quote@example.com")
    signal = _open_long(db_session, user_id=user.id)
    _install(monkeypatch, db_session, quote=None)

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "completed"
    assert result["evaluated"] == 0
    assert result["transitions"] == 0

    db_session.expire_all()
    refreshed = db_session.scalar(select(Signal).where(Signal.id == signal.id))
    assert refreshed is not None
    assert refreshed.state == "new"
