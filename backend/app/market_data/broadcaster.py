from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.market_data.quotes import MarketQuote, MarketQuotesSnapshot, fetch_market_quotes

logger = logging.getLogger(__name__)


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
