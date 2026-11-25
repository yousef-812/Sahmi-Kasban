"""Order-flow data (order book, trades, whales) for EGX tickers — WP-18/WP-26.

Reality check against the providers configured in this repo (see MARKET_DATA_STRATEGY.md):

- The unified ``MarketDataProvider`` protocol exposes only ``get_history`` candles
  (``app/market_data/types.py``); neither ``TradingViewMarketDataProvider`` nor
  ``YFinanceMarketDataProvider`` implements any depth/trade method.
- The underlying ``TradingViewConnector`` (``reusable_data_fetcher.py``) only
  subscribes the top-of-book quote fields ``lp, ch, chp, v, bid, ask, open_price``:
  single bid/ask prices without sizes, no depth ladder, and no time-and-sales feed.
- The TradingView scanner feed (``quotes.py``) provides session volume/price only.

Depth data is served through the ``DepthProvider`` registry (``depth.py``,
WP-26): with the default ``MARKET_DATA_DEPTH_PROVIDER=none`` the getters below
degrade honestly — ``available: false`` plus a ``reason`` string — instead of
inventing numbers. When a depth-capable provider is configured (today: only the
capability-empty ``tradingview`` skeleton; tomorrow: a licensed feed), its data
is passed through unchanged under the same response keys.

- ``detect_whales`` is a documented *proxy*, not order-flow: it flags trading sessions
  whose daily turnover (close x volume) — computed from cached daily candle snapshots
  and, best-effort, from the live session quote — exceeds a value threshold. The
  threshold is either caller-supplied or 3x the median turnover of the last 60
  sessions. It measures unusual daily activity, not individual large trades.
"""

from __future__ import annotations

import logging
import statistics
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_data.depth import get_depth_provider
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.quotes import fetch_single_quote
from app.market_data.types import (
    DEPTH_CAP_DEPTH,
    DEPTH_CAP_ORDER_BOOK,
    DEPTH_CAP_TRADES,
    DepthProvider,
    DepthSummaryData,
    MarketDataUnavailableError,
    OrderBookData,
    RecentTradeData,
)
from app.models import MarketDataSnapshot

logger = logging.getLogger(__name__)

_WHALE_LOOKBACK_SESSIONS = 60
_WHALE_AUTO_MIN_SESSIONS = 10
_WHALE_AUTO_THRESHOLD_MULTIPLIER = 3.0
_WHALE_MAX_ITEMS = 50

_DEPTH_UNAVAILABLE_REASON = "No depth-capable market-data provider is configured"


def _unavailable_payload(*, reason: str) -> dict[str, object]:
    return {"provider": None, "reason": reason}


def _levels_payload(levels: tuple) -> list[dict[str, float]]:
    return [level.to_dict() for level in levels]


def _as_positive_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _as_non_negative_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _session_date_iso(timestamp: object) -> str | None:
    if not isinstance(timestamp, str):
        return None
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def _daily_turnover_sessions(db: Session, ticker: str) -> list[dict[str, object]]:
    snapshots = db.scalars(
        select(MarketDataSnapshot)
        .where(
            MarketDataSnapshot.ticker == ticker,
            MarketDataSnapshot.interval == "1d",
        )
        .order_by(MarketDataSnapshot.fetched_at.desc())
    ).all()
    best_candles: list[object] = []
    for snapshot in snapshots:
        payload = snapshot.payload if isinstance(snapshot.payload, dict) else {}
        candles = payload.get("candles")
        if isinstance(candles, list) and len(candles) > len(best_candles):
            best_candles = candles

    sessions: dict[object, dict[str, object]] = {}
    for position, candle in enumerate(best_candles):
        if not isinstance(candle, dict):
            continue
        close = _as_positive_float(candle.get("close"))
        volume = _as_non_negative_float(candle.get("volume"))
        if close is None or volume is None:
            continue
        session_date = _session_date_iso(candle.get("timestamp"))
        key: object = session_date if session_date is not None else position
        sessions[key] = {
            "session_date": session_date,
            "close": close,
            "volume": volume,
            "turnover_egp": close * volume,
        }
    return list(sessions.values())


async def _live_session_turnover(db: Session, ticker: str) -> dict[str, object] | None:
    try:
        quote = await fetch_single_quote(db, ticker)
    except Exception as exc:
        logger.warning("Whale proxy could not fetch the live quote for %s: %s", ticker, exc)
        return None
    if quote is None:
        return None
    price = _as_positive_float(quote.current_price)
    volume = _as_non_negative_float(quote.volume)
    if price is None or volume is None:
        return None
    return {
        "session_date": quote.session_date,
        "close": price,
        "volume": volume,
        "turnover_egp": price * volume,
    }


def _merge_live_session(sessions: list[dict[str, object]], live: dict[str, object]) -> None:
    live_date = live.get("session_date")
    if live_date is not None:
        for index, session in enumerate(sessions):
            if session.get("session_date") == live_date:
                sessions[index] = live
                return
    sessions.append(live)


def _recent_median_turnover(sessions: list[dict[str, object]]) -> float | None:
    turnovers = [
        float(session["turnover_egp"]) for session in sessions if float(session["turnover_egp"]) > 0
    ][-_WHALE_LOOKBACK_SESSIONS:]
    if len(turnovers) < _WHALE_AUTO_MIN_SESSIONS:
        return None
    return statistics.median(turnovers)


def _provider_or_reason(
    provider: DepthProvider | None, capability: str
) -> tuple[DepthProvider | None, str | None]:
    if provider is None:
        return None, _DEPTH_UNAVAILABLE_REASON
    if capability not in provider.capabilities:
        return None, f"Provider {provider.name!r} does not support {capability!r}"
    return provider, None


async def _call_provider(fetcher, fallback_ticker: str):
    try:
        return await fetcher(), None
    except MarketDataUnavailableError as exc:
        logger.warning("Depth provider call failed for %s: %s", fallback_ticker, exc)
        return None, str(exc)


async def get_order_book(db: Session, ticker: str) -> dict[str, object]:
    """Return the level-2 order book for a ticker.

    Routed through the configured ``DepthProvider`` (WP-26). With no
    depth-capable provider the response reports ``available: false`` plus a
    ``reason`` rather than fabricating levels.
    """
    normalized = normalize_egx_ticker(ticker)
    provider, reason = _provider_or_reason(get_depth_provider(), DEPTH_CAP_ORDER_BOOK)
    if provider is None:
        return {
            "available": False,
            "ticker": normalized,
            "as_of": None,
            "bids": [],
            "asks": [],
            **_unavailable_payload(reason=reason or _DEPTH_UNAVAILABLE_REASON),
        }

    data, error = await _call_provider(lambda: provider.get_order_book(normalized), normalized)
    if isinstance(data, OrderBookData):
        return {
            "available": True,
            "ticker": normalized,
            "as_of": data.as_of,
            "bids": _levels_payload(data.bids),
            "asks": _levels_payload(data.asks),
            "provider": provider.name,
            "reason": None,
        }
    return {
        "available": False,
        "ticker": normalized,
        "as_of": None,
        "bids": [],
        "asks": [],
        **_unavailable_payload(reason=error or _DEPTH_UNAVAILABLE_REASON),
    }


async def get_recent_trades(db: Session, ticker: str, *, limit: int = 200) -> dict[str, object]:
    """Return recent executed trades (time & sales) for a ticker.

    Routed through the configured ``DepthProvider`` (WP-26). ``limit`` is
    accepted for contract compatibility and validated at the API layer.
    """
    normalized = normalize_egx_ticker(ticker)
    provider, reason = _provider_or_reason(get_depth_provider(), DEPTH_CAP_TRADES)
    if provider is None:
        return {
            "available": False,
            "ticker": normalized,
            "items": [],
            **_unavailable_payload(reason=reason or _DEPTH_UNAVAILABLE_REASON),
        }

    data, error = await _call_provider(
        lambda: provider.get_recent_trades(normalized, limit=limit),
        normalized,
    )
    if isinstance(data, RecentTradeData):
        return {
            "available": True,
            "ticker": normalized,
            "items": [item.to_dict() for item in data.items],
            "provider": provider.name,
            "reason": None,
        }
    return {
        "available": False,
        "ticker": normalized,
        "items": [],
        **_unavailable_payload(reason=error or _DEPTH_UNAVAILABLE_REASON),
    }


async def get_market_depth(db: Session, ticker: str, *, levels: int = 10) -> dict[str, object]:
    """Return an aggregated market-depth summary for a ticker.

    Same routing and honesty rules as ``get_order_book`` (WP-26).
    """
    normalized = normalize_egx_ticker(ticker)
    provider, reason = _provider_or_reason(get_depth_provider(), DEPTH_CAP_DEPTH)
    if provider is None:
        return {
            "available": False,
            "ticker": normalized,
            "as_of": None,
            "levels": levels,
            "bid_levels": [],
            "ask_levels": [],
            "total_bid_volume": 0.0,
            "total_ask_volume": 0.0,
            "spread": None,
            "mid_price": None,
            **_unavailable_payload(reason=reason or _DEPTH_UNAVAILABLE_REASON),
        }

    data, error = await _call_provider(
        lambda: provider.get_market_depth(normalized, levels=levels),
        normalized,
    )
    if isinstance(data, DepthSummaryData):
        return {
            "available": True,
            "ticker": normalized,
            "as_of": data.as_of,
            "levels": levels,
            "bid_levels": _levels_payload(data.bid_levels),
            "ask_levels": _levels_payload(data.ask_levels),
            "total_bid_volume": round(data.total_bid_volume, 6),
            "total_ask_volume": round(data.total_ask_volume, 6),
            "spread": data.spread,
            "mid_price": data.mid_price,
            "provider": provider.name,
            "reason": None,
        }
    return {
        "available": False,
        "ticker": normalized,
        "as_of": None,
        "levels": levels,
        "bid_levels": [],
        "ask_levels": [],
        "total_bid_volume": 0.0,
        "total_ask_volume": 0.0,
        "spread": None,
        "mid_price": None,
        **_unavailable_payload(reason=error or _DEPTH_UNAVAILABLE_REASON),
    }


async def detect_whales(
    db: Session,
    ticker: str,
    *,
    value_threshold: float | None = None,
) -> dict[str, object]:
    """Flag unusually high-turnover sessions for a ticker (whale-activity *proxy*).

    This is not order-flow: individual trades are unavailable, so a session whose
    turnover (close x volume) crosses ``value_threshold`` (EGP, caller-supplied) or
    3x the median turnover of the last 60 available sessions is reported as a coarse
    whale-activity signal. Sources: cached daily candle snapshots plus the best-effort
    live quote session. ``available`` is false when no threshold can be resolved.
    """
    normalized = normalize_egx_ticker(ticker)
    sessions = _daily_turnover_sessions(db, normalized)
    live_session = await _live_session_turnover(db, normalized)
    if live_session is not None:
        _merge_live_session(sessions, live_session)

    median_turnover = _recent_median_turnover(sessions)
    threshold: float | None = None
    if value_threshold is not None and value_threshold > 0:
        threshold = float(value_threshold)
    elif median_turnover is not None:
        threshold = round(median_turnover * _WHALE_AUTO_THRESHOLD_MULTIPLIER, 6)

    if threshold is None or not sessions:
        return {"available": False, "ticker": normalized, "threshold": None, "items": []}

    items: list[dict[str, object]] = []
    for session in reversed(sessions):
        turnover = float(session["turnover_egp"])
        if turnover < threshold:
            continue
        ratio = round(turnover / median_turnover, 4) if median_turnover else None
        items.append(
            {
                "session_date": session["session_date"],
                "close": session["close"],
                "volume": session["volume"],
                "turnover_egp": round(turnover, 2),
                "turnover_ratio": ratio,
            }
        )
        if len(items) >= _WHALE_MAX_ITEMS:
            break

    return {
        "available": True,
        "ticker": normalized,
        "threshold": threshold,
        "items": items,
    }
