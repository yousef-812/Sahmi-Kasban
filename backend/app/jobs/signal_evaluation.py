from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Environment, get_settings
from app.db.session import SessionLocal
from app.market_calendar import EGXTradingCalendar
from app.market_data.broadcaster import (
    build_alert_created_payload,
    build_signal_updated_payload,
    get_analysis_broadcaster,
)
from app.market_data.quotes import fetch_single_quote
from app.models import Alert, Signal, SignalEvent, User
from app.services.signal_lifecycle import advance_signal, close_signal

logger = logging.getLogger(__name__)

_TERMINAL_STATES = frozenset({"closed", "expired"})

_last_started: float | None = None


def _trading_session_now() -> bool:
    calendar = EGXTradingCalendar.from_settings()
    local = datetime.now(UTC).astimezone(calendar.timezone)
    return calendar.is_trading_session(local.date())


def _alert_user_ids(db: Session, signal: Signal) -> list[UUID]:
    if signal.user_id is not None:
        return [signal.user_id]
    return list(
        db.scalars(
            select(User.id).where(User.status == "active", User.email_verified.is_(True))
        ).all()
    )


def _publish_signal_updated_events(signal: Signal, events: list[SignalEvent]) -> None:
    """Fire-and-forget ``signal.updated`` broadcast; never raises into the job."""
    try:
        broadcaster = get_analysis_broadcaster()
        for event in events:
            broadcaster.publish_signal_updated(build_signal_updated_payload(signal, event))
    except Exception:
        logger.exception("Failed to publish signal.updated for %s", signal.ticker)


def _publish_alert_created_events(alerts: list[Alert]) -> None:
    """Fire-and-forget ``alert.created`` delivery; never raises into the job."""
    if not alerts:
        return
    try:
        broadcaster = get_analysis_broadcaster()
        for alert in alerts:
            broadcaster.publish_alert_created(build_alert_created_payload(alert))
    except Exception:
        logger.exception("Failed to publish alert.created events")


def create_transition_alerts(db: Session, signal: Signal, events: list[SignalEvent]) -> int:
    """Insert one alert per transition event for every interested user."""
    if not events:
        return 0
    user_ids = _alert_user_ids(db, signal)
    if not user_ids:
        return 0
    created = 0
    alerts: list[Alert] = []
    for event in events:
        title = f"{signal.ticker} {event.event}"[:160]
        price = event.price if event.price is not None else signal.entry
        body = (
            f"إشارة {signal.direction} على {signal.ticker} — "
            f"{event.event} عند {price}."
        )
        if event.note:
            body = f"{body} {event.note}"
        for user_id in user_ids:
            alert = Alert(
                user_id=user_id,
                type="signal_transition",
                ref_id=signal.id,
                title=title,
                body=body[:2000],
            )
            db.add(alert)
            alerts.append(alert)
            created += 1
    db.commit()
    _publish_alert_created_events(alerts)
    return created


def _candle_from_quote(quote: object) -> tuple[float, float, float] | None:
    close = getattr(quote, "current_price", None)
    if close is None:
        return None
    high = getattr(quote, "session_high", None)
    low = getattr(quote, "session_low", None)
    return (
        float(high) if high is not None else float(close),
        float(low) if low is not None else float(close),
        float(close),
    )


async def run_signal_evaluation() -> dict[str, object]:
    """Evaluate every non-terminal signal against the latest quote.

    Idempotent by design: the state machine never applies a transition twice,
    and alerts are only inserted when ``advance_signal`` emits events. The run
    is throttled to at most one evaluation per ``signal_evaluation_minutes``.
    """
    global _last_started
    settings = get_settings()
    if settings.app_env is Environment.TEST:
        return {"status": "skipped", "reason": "test_environment", "evaluated": 0, "alerts": 0}
    if not settings.signal_evaluation_enabled:
        return {"status": "skipped", "reason": "disabled", "evaluated": 0, "alerts": 0}
    interval = settings.signal_evaluation_minutes * 60
    now = time.monotonic()
    if _last_started is not None and now - _last_started < interval:
        return {"status": "skipped", "reason": "throttled", "evaluated": 0, "alerts": 0}
    _last_started = now
    if not _trading_session_now():
        return {"status": "skipped", "reason": "non_trading_session", "evaluated": 0, "alerts": 0}

    evaluated = 0
    transitions = 0
    closed_count = 0
    alerts_created = 0
    failed = 0
    with SessionLocal() as db:
        signals = list(
            db.scalars(
                select(Signal).where(Signal.state.notin_(sorted(_TERMINAL_STATES)))
            ).all()
        )
        for signal in signals:
            try:
                quote = await fetch_single_quote(db, signal.ticker)
            except Exception:
                db.rollback()
                failed += 1
                logger.exception("Signal evaluation quote fetch failed for %s", signal.ticker)
                continue
            candle = _candle_from_quote(quote)
            if candle is None:
                continue
            high, low, close = candle
            try:
                events = advance_signal(db, signal, high=high, low=low, close=close)
            except Exception:
                db.rollback()
                failed += 1
                logger.exception("Signal evaluation failed for %s", signal.ticker)
                continue
            evaluated += 1
            if events:
                transitions += 1
                _publish_signal_updated_events(signal, events)
                alerts_created += create_transition_alerts(db, signal, events)
            if signal.state == "tsl":
                try:
                    reason = events[-1].note if events else "stop hit"
                    exit_price = (
                        float(events[-1].price)
                        if events and events[-1].price is not None
                        else close
                    )
                    close_signal(db, signal, reason=reason or "stop hit", price=exit_price)
                except Exception:
                    db.rollback()
                    failed += 1
                    logger.exception("Signal close failed for %s", signal.ticker)
                    continue
                closed_count += 1
                exit_event = signal.events[-1]
                _publish_signal_updated_events(signal, [exit_event])
                alerts_created += create_transition_alerts(db, signal, [exit_event])

    payload: dict[str, object] = {
        "status": "completed",
        "evaluated": evaluated,
        "transitions": transitions,
        "closed": closed_count,
        "alerts": alerts_created,
        "failed": failed,
        "as_of": datetime.now(UTC).isoformat(),
    }
    logger.info("Signal evaluation result: %s", payload)
    return payload


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(asyncio.run(run_signal_evaluation()), ensure_ascii=False))


if __name__ == "__main__":
    main()
