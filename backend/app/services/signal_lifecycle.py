"""Signal lifecycle state machine (new -> buy -> t1done -> t2done -> t3done -> tsl -> closed).

Pure domain logic: no network access and no scheduler; every function takes an
explicit ``Session`` and persists through it. One ``SignalEvent`` is written per
applied transition. The trailing stop lives in ``Signal.meta``:
  - ``activation_high``: running best extreme observed since target-1 activation
    (highest ``high`` for long, lowest ``low`` for short).
  - ``trailing_stop``: ratcheted stop level, trailing the activation extreme by
    the initial risk distance (``entry - stop`` for long, ``stop - entry`` for short).
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.signals import Signal, SignalEvent

SIGNAL_STATES = frozenset({"new", "buy", "t1done", "t2done", "t3done", "tsl", "closed", "expired"})

_STATE_TRANSITIONS: dict[str, frozenset[str]] = {
    "new": frozenset({"buy", "closed"}),
    "buy": frozenset({"t1done", "tsl", "closed"}),
    "t1done": frozenset({"t2done", "tsl", "closed"}),
    "t2done": frozenset({"t3done", "tsl", "closed"}),
    "t3done": frozenset({"tsl", "closed"}),
    "tsl": frozenset({"closed"}),
    "closed": frozenset(),
    "expired": frozenset(),
}

_TARGET_STATES = frozenset({"buy", "t1done", "t2done", "t3done"})
_TRAILING_STATES = frozenset({"t1done", "t2done", "t3done"})
_NEXT_STATE = {"buy": "t1done", "t1done": "t2done", "t2done": "t3done"}
_TARGET_ATTR = {"t1done": "t1", "t2done": "t2", "t3done": "t3"}
_PNL_QUANTUM = Decimal("0.0001")


class InvalidSignalTransition(RuntimeError):
    """Raised when a caller attempts an explicit transition the state machine does not allow."""


def state_transitions() -> dict[str, set[str]]:
    """Return the allowed transition map (used by docs and tests)."""
    return {state: set(targets) for state, targets in _STATE_TRANSITIONS.items()}


def _decimal(value: object) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric value: {value!r}") from exc
    return result


def _moment() -> datetime:
    return datetime.now(UTC)


def _is_long(signal: Signal) -> bool:
    return signal.direction != "short"


def _meta(signal: Signal) -> dict:
    meta = signal.meta
    return dict(meta) if isinstance(meta, dict) else {}


def _record(signal: Signal, *, event: str, price: Decimal | None, note: str | None) -> SignalEvent:
    item = SignalEvent(signal_id=signal.id, event=event, price=price, note=note)
    signal.events.append(item)
    return item


def _transition(signal: Signal, new_state: str, *, price: Decimal | None, note: str | None) -> SignalEvent:
    allowed = _STATE_TRANSITIONS.get(signal.state, frozenset())
    if new_state not in allowed:
        raise InvalidSignalTransition(f"Transition {signal.state!r} -> {new_state!r} is not allowed")
    signal.state = new_state
    return _record(signal, event=new_state, price=price, note=note)


def _entry_reached(signal: Signal, *, high: Decimal, low: Decimal) -> bool:
    if _is_long(signal):
        return high >= signal.entry
    return low <= signal.entry


def _target_reached(target: Decimal, *, close: Decimal, is_long: bool) -> bool:
    return close >= target if is_long else close <= target


def _stop_hit(stop: Decimal, *, high: Decimal, low: Decimal, is_long: bool) -> bool:
    return low <= stop if is_long else high >= stop


def _current_stop(signal: Signal) -> Decimal:
    trailing = _meta(signal).get("trailing_stop")
    if trailing is not None:
        return _decimal(trailing)
    return _decimal(signal.stop)


def _ratchet_trailing(signal: Signal, *, high: Decimal, low: Decimal) -> None:
    """Update ``activation_high``/``trailing_stop`` for a signal at or beyond t1done."""
    meta = _meta(signal)
    is_long = _is_long(signal)
    extreme = high if is_long else low
    stored = meta.get("activation_high")
    if stored is None:
        activation = extreme
    elif is_long:
        activation = max(_decimal(stored), extreme)
    else:
        activation = min(_decimal(stored), extreme)
    risk = abs(_decimal(signal.entry) - _decimal(signal.stop))
    trailing = activation - risk if is_long else activation + risk
    previous = meta.get("trailing_stop")
    if previous is not None:
        prior = _decimal(previous)
        trailing = max(trailing, prior) if is_long else min(trailing, prior)
    signal.meta = {
        **meta,
        "activation_high": float(activation),
        "trailing_stop": float(trailing),
    }


def _target_value(signal: Signal, next_state: str) -> Decimal | None:
    raw = getattr(signal, _TARGET_ATTR[next_state], None)
    return None if raw is None else _decimal(raw)


def open_signal(
    db: Session,
    *,
    ticker: str,
    direction: str,
    entry: float,
    stop: float,
    targets: tuple[float, float, float],
    source: str,
    user_id: UUID | None = None,
    ref_report_id: UUID | None = None,
) -> Signal:
    """Create a new signal in state ``new`` with an initial ``opened`` event."""
    direction_norm = direction.strip().lower()
    if direction_norm not in {"long", "short"}:
        raise ValueError(f"Unsupported signal direction: {direction!r}")
    entry_dec = _decimal(entry)
    if entry_dec <= 0:
        raise ValueError("Signal entry must be positive")
    t1, t2, t3 = targets
    signal = Signal(
        ticker=ticker,
        direction=direction_norm,
        entry=entry_dec,
        stop=_decimal(stop),
        t1=None if t1 is None else _decimal(t1),
        t2=None if t2 is None else _decimal(t2),
        t3=None if t3 is None else _decimal(t3),
        state="new",
        source=source,
        user_id=user_id,
        ref_report_id=ref_report_id,
        meta={},
    )
    db.add(signal)
    db.flush()
    _record(signal, event="opened", price=entry_dec, note=None)
    db.commit()
    return signal


def advance_signal(
    db: Session,
    signal: Signal,
    *,
    high: float,
    low: float,
    close: float,
) -> list[SignalEvent]:
    """Evaluate the state machine against one candle and apply every applicable transition.

    Transitions are applied in order (entry -> buy, targets t1/t2/t3, trailing stop)
    and never move backwards. The stop is checked once per candle with the level in
    force at the start of the candle; the trailing stop activates from the following
    candle after target-1. Tolerant by design: never raises for out-of-range prices.
    """
    high_dec = _decimal(high)
    low_dec = _decimal(low)
    close_dec = _decimal(close)
    is_long = _is_long(signal)
    events: list[SignalEvent] = []
    changed = False

    if signal.state == "new" and _entry_reached(signal, high=high_dec, low=low_dec):
        events.append(
            _transition(signal, "buy", price=close_dec, note=f"entry {_decimal(signal.entry)} reached")
        )
        changed = True

    if signal.state in _TARGET_STATES:
        stop = _current_stop(signal)
        if _stop_hit(stop, high=high_dec, low=low_dec, is_long=is_long):
            note = "trailing stop hit" if "trailing_stop" in _meta(signal) else "stop loss hit"
            events.append(_transition(signal, "tsl", price=stop, note=note))
            changed = True
        else:
            while (next_state := _NEXT_STATE.get(signal.state)) is not None:
                target = _target_value(signal, next_state)
                if target is None or not _target_reached(target, close=close_dec, is_long=is_long):
                    break
                events.append(
                    _transition(signal, next_state, price=close_dec, note=f"target {target} reached")
                )
                changed = True
            if signal.state in _TRAILING_STATES:
                _ratchet_trailing(signal, high=high_dec, low=low_dec)
                changed = True

    if changed:
        signal.updated_at = _moment()
        db.commit()
    return events


def close_signal(db: Session, signal: Signal, *, reason: str, price: float) -> Signal:
    """Close a signal at ``price``, computing the signed percentage PnL from entry."""
    if "closed" not in _STATE_TRANSITIONS.get(signal.state, frozenset()):
        raise InvalidSignalTransition(f"Cannot close a signal in state {signal.state!r}")
    price_dec = _decimal(price)
    entry = _decimal(signal.entry)
    if _is_long(signal):
        pnl = (price_dec - entry) / entry * Decimal("100")
    else:
        pnl = (entry - price_dec) / entry * Decimal("100")
    moment = _moment()
    signal.pnl_pct = pnl.quantize(_PNL_QUANTUM, rounding=ROUND_HALF_UP)
    signal.state = "closed"
    signal.closed_at = moment
    signal.updated_at = moment
    _record(signal, event="closed", price=price_dec, note=reason[:255])
    db.commit()
    return signal
