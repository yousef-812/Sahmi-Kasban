from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.market_data.quotes import MarketQuote, MarketQuotesSnapshot, fetch_market_quotes
from app.models.signals import Alert, Signal, SignalEvent

logger = logging.getLogger(__name__)

ANALYSIS_EVENT_SIGNAL_UPDATED = "signal.updated"
ANALYSIS_EVENT_ALERT_CREATED = "alert.created"
ANALYSIS_STREAM_HEARTBEAT_SECONDS = 20.0
ANALYSIS_STREAM_QUEUE_MAXSIZE = 64


def _quote_to_dict(quote: MarketQuote) -> dict[str, Any]:
    return quote.to_dict()


def _snapshot_to_dict(snapshot: MarketQuotesSnapshot) -> dict[str, Any]:
    return {
        "type": "snapshot",
        "source": snapshot.source,
        "generated_at": snapshot.generated_at.isoformat(),
        "market_open": snapshot.market_open,
        "next_session_open": snapshot.next_session_open.isoformat() if snapshot.next_session_open else None,
        "items": [_quote_to_dict(item) for item in snapshot.items],
    }


class QuoteBroadcaster:
    """Manages real-time quote broadcast via WebSockets to connected mobile clients."""

    def __init__(self) -> None:
        self._active_connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._last_snapshot: MarketQuotesSnapshot | None = None
        self._last_quotes_map: dict[str, MarketQuote] = {}

    @property
    def connection_count(self) -> int:
        return len(self._active_connections)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._active_connections.add(websocket)
            logger.info("WebSocket client connected. Active connections: %s", len(self._active_connections))

        # Send immediate cached snapshot if available
        snapshot = self._last_snapshot
        if snapshot is None:
            try:
                with SessionLocal() as db:
                    snapshot = await fetch_market_quotes(db, force_refresh=False)
                    self._last_snapshot = snapshot
                    self._last_quotes_map = {q.ticker: q for q in snapshot.items}
            except Exception:
                logger.exception("Error fetching initial quotes for new WebSocket client")

        if snapshot is not None:
            try:
                await websocket.send_json(_snapshot_to_dict(snapshot))
            except Exception:
                await self.disconnect(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._active_connections.discard(websocket)
            logger.info(
                "WebSocket client disconnected. Active connections: %s", len(self._active_connections)
            )

    async def broadcast_snapshot(self, snapshot: MarketQuotesSnapshot) -> None:
        payload = _snapshot_to_dict(snapshot)
        async with self._lock:
            connections = list(self._active_connections)

        if not connections:
            return

        dead_connections: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(payload)
            except (WebSocketDisconnect, RuntimeError, Exception):
                dead_connections.append(ws)

        if dead_connections:
            async with self._lock:
                for ws in dead_connections:
                    self._active_connections.discard(ws)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("QuoteBroadcaster background loop started")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("QuoteBroadcaster background loop stopped")

    async def _run_loop(self) -> None:
        settings = get_settings()
        poll_interval = max(3.0, settings.market_quotes_refresh_seconds)

        while self._running:
            try:
                has_subscribers = len(self._active_connections) > 0
                with SessionLocal() as db:
                    snapshot = await fetch_market_quotes(db, force_refresh=has_subscribers)
                    self._last_snapshot = snapshot

                    new_map = {q.ticker: q for q in snapshot.items}
                    has_changes = False
                    if len(new_map) != len(self._last_quotes_map):
                        has_changes = True
                    else:
                        for ticker, new_q in new_map.items():
                            old_q = self._last_quotes_map.get(ticker)
                            if (
                                old_q is None
                                or old_q.current_price != new_q.current_price
                                or old_q.change != new_q.change
                                or old_q.volume != new_q.volume
                            ):
                                has_changes = True
                                break

                    self._last_quotes_map = new_map

                    if has_subscribers and has_changes:
                        await self.broadcast_snapshot(snapshot)

                if not snapshot.market_open and not has_subscribers:
                    await asyncio.sleep(30.0)
                else:
                    await asyncio.sleep(poll_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in QuoteBroadcaster background loop")
                await asyncio.sleep(5.0)


_quote_broadcaster: QuoteBroadcaster | None = None


def get_quote_broadcaster() -> QuoteBroadcaster:
    global _quote_broadcaster
    if _quote_broadcaster is None:
        _quote_broadcaster = QuoteBroadcaster()
    return _quote_broadcaster


def build_signal_updated_payload(signal: Signal, event: SignalEvent) -> dict[str, Any]:
    """Serialize a signal transition into the ``signal.updated`` wire payload."""
    created_at = event.created_at if event.created_at is not None else datetime.now(UTC)
    return {
        "type": ANALYSIS_EVENT_SIGNAL_UPDATED,
        "signal_id": str(signal.id),
        "ticker": signal.ticker,
        "direction": signal.direction,
        "state": signal.state,
        "event": event.event,
        "price": float(event.price) if event.price is not None else None,
        "note": event.note,
        "pnl_pct": float(signal.pnl_pct) if signal.pnl_pct is not None else None,
        "user_id": str(signal.user_id) if signal.user_id is not None else None,
        "created_at": created_at.isoformat(),
    }


def build_alert_created_payload(alert: Alert) -> dict[str, Any]:
    """Serialize a persisted alert into the ``alert.created`` wire payload."""
    created_at = alert.created_at if alert.created_at is not None else datetime.now(UTC)
    return {
        "type": ANALYSIS_EVENT_ALERT_CREATED,
        "alert_id": str(alert.id),
        "alert_type": alert.type,
        "ref_id": str(alert.ref_id) if alert.ref_id is not None else None,
        "title": alert.title,
        "body": alert.body,
        "is_read": alert.is_read,
        "user_id": str(alert.user_id),
        "created_at": created_at.isoformat(),
    }


@dataclass(eq=False)
class AnalysisSubscriber:
    """One connected analysis-stream listener backed by a bounded queue."""

    queue: asyncio.Queue[dict[str, Any]]
    user_id: UUID | None
    loop: asyncio.AbstractEventLoop


class AnalysisBroadcaster:
    """Fan-out of signal/alert events to subscribed WebSockets.

    Publishing is fire-and-forget: events are offered to each subscriber's
    bounded queue with ``put_nowait`` semantics, so a slow consumer only loses
    its own events (dropped + logged) and never blocks the producer. No
    background task is required — each WebSocket endpoint pumps its own queue.
    """

    def __init__(self) -> None:
        self._subscribers: set[AnalysisSubscriber] = set()
        self.heartbeat_seconds: float = ANALYSIS_STREAM_HEARTBEAT_SECONDS
        self.dropped_events: int = 0

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    async def subscribe(self, *, user_id: UUID | None = None) -> AnalysisSubscriber:
        subscriber = AnalysisSubscriber(
            queue=asyncio.Queue(maxsize=ANALYSIS_STREAM_QUEUE_MAXSIZE),
            user_id=user_id,
            loop=asyncio.get_running_loop(),
        )
        self._subscribers.add(subscriber)
        logger.info(
            "Analysis stream subscriber added. Active subscribers: %s", len(self._subscribers)
        )
        return subscriber

    async def unsubscribe(self, subscriber: AnalysisSubscriber) -> None:
        self._subscribers.discard(subscriber)
        logger.info(
            "Analysis stream subscriber removed. Active subscribers: %s", len(self._subscribers)
        )

    def publish_signal_updated(self, payload: dict[str, Any]) -> None:
        """Broadcast a ``signal.updated`` event to every subscriber."""
        self._fanout(lambda _subscriber: True, payload)

    def publish_alert_created(self, payload: dict[str, Any]) -> None:
        """Deliver an ``alert.created`` event only to its owning user's subscribers."""
        user_id = payload.get("user_id")
        self._fanout(
            lambda subscriber: subscriber.user_id is not None and str(subscriber.user_id) == user_id,
            payload,
        )

    async def pump(self, websocket: WebSocket, subscriber: AnalysisSubscriber) -> None:
        """Forward queued events to ``websocket``, emitting heartbeat pings when idle.

        Returns when the socket can no longer be written to; the caller owns
        cancellation and subscriber cleanup.
        """
        while True:
            try:
                payload = await asyncio.wait_for(subscriber.queue.get(), timeout=self.heartbeat_seconds)
            except TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                continue
            try:
                await websocket.send_json(payload)
            except Exception:
                break

    def _fanout(self, predicate, payload: dict[str, Any]) -> None:
        for subscriber in list(self._subscribers):
            if predicate(subscriber):
                self._offer(subscriber, payload)

    def _offer(self, subscriber: AnalysisSubscriber, payload: dict[str, Any]) -> None:
        queue = subscriber.queue
        if queue.full():
            self._drop(subscriber, payload)
            return
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None
        if running_loop is subscriber.loop:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                self._drop(subscriber, payload)
            return
        try:
            subscriber.loop.call_soon_threadsafe(self._put_nowait, queue, payload)
        except RuntimeError:
            self._drop(subscriber, payload)

    @staticmethod
    def _put_nowait(queue: asyncio.Queue[dict[str, Any]], payload: dict[str, Any]) -> None:
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            logger.warning("Analysis stream queue full; dropping event of type %s", payload.get("type"))

    def _drop(self, subscriber: AnalysisSubscriber, payload: dict[str, Any]) -> None:
        self.dropped_events += 1
        logger.warning(
            "Analysis stream slow consumer; dropping event of type %s (dropped total: %s)",
            payload.get("type"),
            self.dropped_events,
        )


_analysis_broadcaster: AnalysisBroadcaster | None = None


def get_analysis_broadcaster() -> AnalysisBroadcaster:
    global _analysis_broadcaster
    if _analysis_broadcaster is None:
        _analysis_broadcaster = AnalysisBroadcaster()
    return _analysis_broadcaster
