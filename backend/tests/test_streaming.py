from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from starlette.websockets import WebSocketDisconnect

from app.api.routes import market as market_routes
from app.core.config import Environment
from app.jobs import signal_evaluation
from app.market_data.broadcaster import (
    ANALYSIS_STREAM_QUEUE_MAXSIZE,
    AnalysisBroadcaster,
    get_analysis_broadcaster,
)
from app.models import User
from app.services.signal_lifecycle import open_signal

PASSWORD = "StrongPass123"
STREAM_PATH = "/api/v1/market/analysis/stream"


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


def _install_job(monkeypatch: pytest.MonkeyPatch, db_session: Session, *, quote: SimpleNamespace) -> None:
    factory = sessionmaker(bind=db_session.get_bind(), autoflush=False, expire_on_commit=False)

    async def _stub_quote(_db: Session, ticker: str, *, force_refresh: bool = False):
        return SimpleNamespace(
            ticker=ticker,
            current_price=quote.current_price,
            session_high=quote.session_high,
            session_low=quote.session_low,
        )

    monkeypatch.setattr(signal_evaluation, "SessionLocal", factory)
    monkeypatch.setattr(signal_evaluation, "get_settings", lambda: _StubSettings())
    monkeypatch.setattr(signal_evaluation, "_trading_session_now", lambda: True)
    monkeypatch.setattr(signal_evaluation, "fetch_single_quote", _stub_quote)
    monkeypatch.setattr(signal_evaluation, "_last_started", None, raising=False)


def _install_websocket_session(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> None:
    factory = sessionmaker(bind=db_session.get_bind(), autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(market_routes, "SessionLocal", factory)


def _register_and_login(client: TestClient, fake_email_service, *, email: str) -> str:
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "display_name": "Stream Tester"},
    )
    assert registered.status_code == 201
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verified.status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return login.json()["access_token"]


def _user_by_email(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


def _open_long(db: Session, **overrides) -> object:
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


def test_analysis_stream_delivers_signal_updated_and_alert_after_job(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = _register_and_login(client, fake_email_service, email="stream-owner@example.com")
    user = _user_by_email(db_session, "stream-owner@example.com")
    signal = _open_long(db_session, user_id=user.id)
    _install_job(monkeypatch, db_session, quote=_quote(price=101.0, high=102.0, low=99.0))
    _install_websocket_session(monkeypatch, db_session)
    broadcaster = get_analysis_broadcaster()

    with client.websocket_connect(f"{STREAM_PATH}?token={token}") as ws:
        hello = ws.receive_json()
        assert hello["type"] == "connected"
        assert hello["authenticated"] is True
        assert broadcaster.subscriber_count == 1

        result = asyncio.run(signal_evaluation.run_signal_evaluation())
        assert result["status"] == "completed"
        assert result["transitions"] == 1
        assert result["alerts"] == 1

        signal_msg = ws.receive_json()
        assert signal_msg["type"] == "signal.updated"
        assert signal_msg["signal_id"] == str(signal.id)
        assert signal_msg["ticker"] == "COMI"
        assert signal_msg["direction"] == "long"
        assert signal_msg["state"] == "buy"
        assert signal_msg["event"] == "buy"
        assert signal_msg["price"] == pytest.approx(101.0)
        assert signal_msg["pnl_pct"] is None
        assert signal_msg["user_id"] == str(user.id)
        assert isinstance(signal_msg["created_at"], str)

        alert_msg = ws.receive_json()
        assert alert_msg["type"] == "alert.created"
        assert alert_msg["user_id"] == str(user.id)
        assert alert_msg["alert_type"] == "signal_transition"
        assert alert_msg["ref_id"] == str(signal.id)
        assert alert_msg["title"]
        assert alert_msg["body"]
        assert alert_msg["is_read"] is False

    assert broadcaster.subscriber_count == 0


def test_alert_created_reaches_only_the_authenticated_owner(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token_a = _register_and_login(client, fake_email_service, email="stream-a@example.com")
    token_b = _register_and_login(client, fake_email_service, email="stream-b@example.com")
    user_b = _user_by_email(db_session, "stream-b@example.com")
    signal = _open_long(db_session, user_id=user_b.id)
    _install_job(monkeypatch, db_session, quote=_quote(price=101.0, high=102.0, low=99.0))
    _install_websocket_session(monkeypatch, db_session)
    broadcaster = get_analysis_broadcaster()

    with client.websocket_connect(f"{STREAM_PATH}?token={token_a}") as ws_a, client.websocket_connect(
        f"{STREAM_PATH}?token={token_b}"
    ) as ws_b:
        assert ws_a.receive_json()["type"] == "connected"
        assert ws_b.receive_json()["type"] == "connected"

        result = asyncio.run(signal_evaluation.run_signal_evaluation())
        assert result["alerts"] == 1

        # The signal is owned by B: A sees the public transition only.
        msg_a = ws_a.receive_json()
        assert msg_a["type"] == "signal.updated"

        msg_b = ws_b.receive_json()
        assert msg_b["type"] == "signal.updated"
        alert_b = ws_b.receive_json()
        assert alert_b["type"] == "alert.created"
        assert alert_b["user_id"] == str(user_b.id)
        assert alert_b["ref_id"] == str(signal.id)

        # Sentinel: if an unwanted alert were queued it would arrive before this.
        broadcaster.publish_signal_updated({"type": "signal.updated", "marker": "sentinel"})
        assert ws_a.receive_json().get("marker") == "sentinel"
        assert ws_b.receive_json().get("marker") == "sentinel"

    assert broadcaster.subscriber_count == 0


def test_unauthenticated_subscriber_gets_signal_updated_but_never_alerts(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = _register_and_login(client, fake_email_service, email="stream-anon-owner@example.com")
    user = _user_by_email(db_session, "stream-anon-owner@example.com")
    _open_long(db_session, user_id=user.id)
    _install_job(monkeypatch, db_session, quote=_quote(price=101.0, high=102.0, low=99.0))
    _install_websocket_session(monkeypatch, db_session)
    broadcaster = get_analysis_broadcaster()

    with client.websocket_connect(f"{STREAM_PATH}?token={token}") as _ws_auth, client.websocket_connect(
        STREAM_PATH
    ) as ws_anon:
        hello = ws_anon.receive_json()
        assert hello["type"] == "connected"
        assert hello["authenticated"] is False
        assert _ws_auth.receive_json()["type"] == "connected"

        result = asyncio.run(signal_evaluation.run_signal_evaluation())
        assert result["transitions"] == 1
        assert result["alerts"] == 1

        anon_first = ws_anon.receive_json()
        assert anon_first["type"] == "signal.updated"

        broadcaster.publish_signal_updated({"type": "signal.updated", "marker": "sentinel"})
        anon_next = ws_anon.receive_json()
        assert anon_next.get("marker") == "sentinel"

    assert broadcaster.subscriber_count == 0


def test_invalid_token_rejects_websocket_connection(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"{STREAM_PATH}?token=not-a-valid-jwt"):
            pass
    assert exc_info.value.code == 1008


def test_disconnect_removes_subscriber(client: TestClient) -> None:
    broadcaster = get_analysis_broadcaster()
    assert broadcaster.subscriber_count == 0

    with client.websocket_connect(STREAM_PATH) as ws:
        assert ws.receive_json()["type"] == "connected"
        assert broadcaster.subscriber_count == 1

    assert broadcaster.subscriber_count == 0


def test_heartbeat_ping_is_sent_when_idle(client: TestClient) -> None:
    broadcaster = get_analysis_broadcaster()
    original = broadcaster.heartbeat_seconds
    broadcaster.heartbeat_seconds = 0.05
    try:
        with client.websocket_connect(STREAM_PATH) as ws:
            hello = ws.receive_json()
            assert hello["type"] == "connected"
            assert hello["heartbeat_seconds"] == 0.05
            heartbeat = ws.receive_json()
            assert heartbeat["type"] == "ping"
    finally:
        broadcaster.heartbeat_seconds = original


def test_slow_consumer_drops_events_without_raising() -> None:
    async def scenario() -> tuple[int, int]:
        broadcaster = AnalysisBroadcaster()
        subscriber = await broadcaster.subscribe()
        total = ANALYSIS_STREAM_QUEUE_MAXSIZE + 25
        for seq in range(total):
            broadcaster.publish_signal_updated({"type": "signal.updated", "seq": seq})
        return broadcaster.dropped_events, subscriber.queue.qsize()

    dropped, queued = asyncio.run(scenario())
    assert dropped == 25
    assert queued == ANALYSIS_STREAM_QUEUE_MAXSIZE


def test_publish_to_closed_loop_is_swallowed() -> None:
    broadcaster = AnalysisBroadcaster()

    async def scenario() -> object:
        return await broadcaster.subscribe()

    subscriber = asyncio.run(scenario())
    broadcaster.publish_signal_updated({"type": "signal.updated"})
    assert broadcaster.dropped_events == 1
    assert subscriber.queue.qsize() == 0


def test_job_survives_broadcaster_failure(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _user_or_create(db_session, "stream-resilient@example.com")
    _open_long(db_session, user_id=user.id)
    _install_job(monkeypatch, db_session, quote=_quote(price=101.0, high=102.0, low=99.0))

    def _raise() -> object:
        raise RuntimeError("broadcaster unavailable")

    monkeypatch.setattr(signal_evaluation, "get_analysis_broadcaster", _raise)

    result = asyncio.run(signal_evaluation.run_signal_evaluation())

    assert result["status"] == "completed"
    assert result["transitions"] == 1
    assert result["alerts"] == 1


def _user_or_create(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is not None:
        return user
    user = User(
        email=email,
        password_hash="hashed-password",
        display_name=email.split("@")[0],
        status="active",
        email_verified=True,
    )
    db.add(user)
    db.commit()
    return user
