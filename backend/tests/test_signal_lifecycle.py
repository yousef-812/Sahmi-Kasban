from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.models import Signal
from app.services.signal_lifecycle import (
    InvalidSignalTransition,
    advance_signal,
    close_signal,
    open_signal,
    state_transitions,
)


def _open_long(db: Session, **overrides: Any) -> Signal:
    params: dict[str, Any] = {
        "ticker": "COMI",
        "direction": "long",
        "entry": 100.0,
        "stop": 95.0,
        "targets": (105.0, 110.0, 115.0),
        "source": "manual",
    }
    params.update(overrides)
    return open_signal(db, **params)


def _open_short(db: Session, **overrides: Any) -> Signal:
    params: dict[str, Any] = {
        "ticker": "COMI",
        "direction": "short",
        "entry": 100.0,
        "stop": 105.0,
        "targets": (95.0, 90.0, 85.0),
        "source": "manual",
    }
    params.update(overrides)
    return open_signal(db, **params)


def _event_names(signal: Signal) -> list[str]:
    return [event.event for event in signal.events]


def test_open_signal_creates_new_row_with_opened_event(db_session: Session) -> None:
    signal = _open_long(db_session)

    assert signal.state == "new"
    assert signal.ticker == "COMI"
    assert signal.direction == "long"
    assert signal.entry == Decimal("100")
    assert signal.stop == Decimal("95")
    assert signal.t1 == Decimal("105")
    assert signal.t2 == Decimal("110")
    assert signal.t3 == Decimal("115")
    assert signal.pnl_pct is None
    assert signal.closed_at is None
    assert signal.meta == {}
    assert _event_names(signal) == ["opened"]
    assert signal.events[0].price == Decimal("100")


def test_open_signal_rejects_unknown_direction_and_bad_entry(db_session: Session) -> None:
    with pytest.raises(ValueError):
        _open_long(db_session, direction="sideways")
    with pytest.raises(ValueError):
        _open_long(db_session, entry=0.0)


def test_happy_path_long_reaches_all_targets(db_session: Session) -> None:
    signal = _open_long(db_session)

    first = advance_signal(db_session, signal, high=106.0, low=99.0, close=105.5)
    assert signal.state == "t1done"
    assert [event.event for event in first] == ["buy", "t1done"]

    second = advance_signal(db_session, signal, high=111.0, low=105.0, close=110.5)
    assert signal.state == "t2done"
    assert [event.event for event in second] == ["t2done"]

    third = advance_signal(db_session, signal, high=116.0, low=110.0, close=115.5)
    assert signal.state == "t3done"
    assert [event.event for event in third] == ["t3done"]

    assert _event_names(signal) == ["opened", "buy", "t1done", "t2done", "t3done"]
    assert len(signal.events) == 5


def test_stop_loss_hit_at_buy_goes_tsl(db_session: Session) -> None:
    signal = _open_long(db_session)
    advance_signal(db_session, signal, high=101.0, low=99.0, close=100.5)
    assert signal.state == "buy"

    events = advance_signal(db_session, signal, high=100.0, low=94.5, close=96.0)
    assert signal.state == "tsl"
    assert [event.event for event in events] == ["tsl"]
    assert events[0].note == "stop loss hit"
    assert events[0].price == Decimal("95")
    assert "trailing_stop" not in (signal.meta or {})


def test_trailing_stop_ratchets_then_triggers_tsl(db_session: Session) -> None:
    signal = _open_long(db_session)

    advance_signal(db_session, signal, high=106.0, low=99.0, close=105.5)
    assert signal.state == "t1done"
    assert signal.meta["activation_high"] == 106.0
    assert signal.meta["trailing_stop"] == 101.0

    events = advance_signal(db_session, signal, high=108.0, low=102.0, close=107.0)
    assert signal.state == "t1done"
    assert events == []
    assert signal.meta["activation_high"] == 108.0
    assert signal.meta["trailing_stop"] == 103.0

    events = advance_signal(db_session, signal, high=107.0, low=102.5, close=104.0)
    assert signal.state == "tsl"
    assert [event.event for event in events] == ["tsl"]
    assert events[0].note == "trailing stop hit"
    assert events[0].price == Decimal("103")


def test_trailing_stop_never_ratchets_downwards(db_session: Session) -> None:
    signal = _open_long(db_session)
    advance_signal(db_session, signal, high=110.0, low=100.0, close=106.0)
    assert signal.meta["trailing_stop"] == 105.0

    advance_signal(db_session, signal, high=107.0, low=106.0, close=106.5)
    assert signal.meta["activation_high"] == 110.0
    assert signal.meta["trailing_stop"] == 105.0


def test_no_transitions_after_tsl_or_closed(db_session: Session) -> None:
    signal = _open_long(db_session)
    advance_signal(db_session, signal, high=101.0, low=94.0, close=96.0)
    assert signal.state == "tsl"

    assert advance_signal(db_session, signal, high=200.0, low=150.0, close=190.0) == []
    assert signal.state == "tsl"

    close_signal(db_session, signal, reason="trailing stop exit", price=96.0)
    assert signal.state == "closed"
    assert advance_signal(db_session, signal, high=300.0, low=250.0, close=280.0) == []
    assert signal.state == "closed"


def test_no_backwards_transitions_within_targets(db_session: Session) -> None:
    signal = _open_long(db_session)
    advance_signal(db_session, signal, high=116.0, low=100.0, close=115.5)
    assert signal.state == "t3done"

    assert advance_signal(db_session, signal, high=200.0, low=112.0, close=190.0) == []
    assert signal.state == "t3done"


def test_nullable_targets_are_skipped(db_session: Session) -> None:
    signal = _open_long(db_session, targets=(105.0, None, None))

    advance_signal(db_session, signal, high=106.0, low=99.0, close=105.5)
    assert signal.state == "t1done"

    events = advance_signal(db_session, signal, high=200.0, low=104.0, close=190.0)
    assert events == []
    assert signal.state == "t1done"

    close_signal(db_session, signal, reason="manual exit", price=190.0)
    assert signal.pnl_pct == Decimal("90.0000")


def test_close_signal_pnl_long_and_short(db_session: Session) -> None:
    long_signal = _open_long(db_session)
    advance_signal(db_session, long_signal, high=101.0, low=99.0, close=100.5)
    closed = close_signal(db_session, long_signal, reason="target miss", price=110.0)

    assert closed.state == "closed"
    assert closed.closed_at is not None
    assert closed.pnl_pct == Decimal("10.0000")
    assert _event_names(closed) == ["opened", "buy", "closed"]
    assert closed.events[-1].note == "target miss"
    assert closed.events[-1].price == Decimal("110")

    short_signal = _open_short(db_session)
    advance_signal(db_session, short_signal, high=99.0, low=96.0, close=96.5)
    short_closed = close_signal(db_session, short_signal, reason="take profit", price=90.0)

    assert short_closed.state == "closed"
    assert short_closed.pnl_pct == Decimal("10.0000")

    losing = _open_short(db_session)
    close_signal(db_session, losing, reason="stop out", price=108.0)
    assert losing.pnl_pct == Decimal("-8.0000")


def test_short_direction_full_lifecycle(db_session: Session) -> None:
    signal = _open_short(db_session)

    events = advance_signal(db_session, signal, high=99.0, low=96.0, close=94.5)
    assert signal.state == "t1done"
    assert [event.event for event in events] == ["buy", "t1done"]
    assert signal.meta["activation_high"] == 96.0
    assert signal.meta["trailing_stop"] == 101.0

    events = advance_signal(db_session, signal, high=95.0, low=88.0, close=89.5)
    assert signal.state == "t2done"
    assert [event.event for event in events] == ["t2done"]
    assert signal.meta["activation_high"] == 88.0
    assert signal.meta["trailing_stop"] == 93.0

    events = advance_signal(db_session, signal, high=94.0, low=91.0, close=92.0)
    assert signal.state == "tsl"
    assert [event.event for event in events] == ["tsl"]
    assert events[0].note == "trailing stop hit"
    assert events[0].price == Decimal("93")


def test_advance_signal_is_tolerant_with_extreme_prices(db_session: Session) -> None:
    signal = _open_long(db_session)

    events = advance_signal(db_session, signal, high=1e9, low=96.0, close=1e9)
    assert signal.state == "t3done"
    assert [event.event for event in events] == ["buy", "t1done", "t2done", "t3done"]

    assert advance_signal(db_session, signal, high=1e9, low=1e9, close=1e9) == []


def test_state_transitions_map_is_complete(db_session: Session) -> None:
    transitions = state_transitions()

    assert set(transitions) == {
        "new",
        "buy",
        "t1done",
        "t2done",
        "t3done",
        "tsl",
        "closed",
        "expired",
    }
    assert transitions["new"] == {"buy", "closed"}
    assert transitions["buy"] == {"t1done", "tsl", "closed"}
    assert transitions["t1done"] == {"t2done", "tsl", "closed"}
    assert transitions["t2done"] == {"t3done", "tsl", "closed"}
    assert transitions["t3done"] == {"tsl", "closed"}
    assert transitions["tsl"] == {"closed"}
    assert transitions["closed"] == set()
    assert transitions["expired"] == set()

    for targets in transitions.values():
        assert targets <= set(transitions)


def test_invalid_signal_transition_on_impossible_close(db_session: Session) -> None:
    signal = _open_long(db_session)
    close_signal(db_session, signal, reason="done", price=100.0)

    with pytest.raises(InvalidSignalTransition):
        close_signal(db_session, signal, reason="double close", price=100.0)

    expired = _open_long(db_session, ticker="SWDY")
    expired.state = "expired"
    db_session.flush()
    with pytest.raises(InvalidSignalTransition):
        close_signal(db_session, expired, reason="expire close", price=100.0)


def test_every_transition_writes_a_signal_event(db_session: Session) -> None:
    signal = _open_long(db_session)
    advance_signal(db_session, signal, high=116.0, low=99.0, close=115.5)
    close_signal(db_session, signal, reason="full run", price=116.0)

    assert _event_names(signal) == ["opened", "buy", "t1done", "t2done", "t3done", "closed"]
    assert all(event.signal_id == signal.id for event in signal.events)


def test_advance_signal_without_changes_does_not_commit(db_session: Session) -> None:
    signal = _open_long(db_session)
    opened_at = signal.updated_at

    events = advance_signal(db_session, signal, high=99.0, low=94.0, close=98.0)
    assert events == []
    assert signal.state == "new"
    assert signal.updated_at == opened_at
