from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
import string
from datetime import UTC, datetime
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from app.core.config import get_settings
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.types import CandleSeries, MarketDataUnavailableError

logger = logging.getLogger(__name__)

TRADINGVIEW_WEBSOCKET_URL = "wss://data.tradingview.com/socket.io/websocket"
TRADINGVIEW_ORIGIN = "https://www.tradingview.com"
TRADINGVIEW_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36"
)
TRADINGVIEW_UNAUTHORIZED_TOKEN = "unauthorized_user_token"


def _session_id(prefix: str) -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{prefix}{suffix}"


def _frame_message(method: str, params: list[object]) -> str:
    payload = json.dumps({"m": method, "p": params}, separators=(",", ":"))
    return f"~m~{len(payload)}~m~{payload}"


def _parse_messages(raw: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    cursor = 0
    marker = "~m~"
    while True:
        start = raw.find(marker, cursor)
        if start < 0:
            break
        length_start = start + len(marker)
        length_end = raw.find(marker, length_start)
        if length_end < 0:
            break
        try:
            payload_length = int(raw[length_start:length_end])
        except ValueError:
            cursor = length_end + len(marker)
            continue
        payload_start = length_end + len(marker)
        payload = raw[payload_start : payload_start + payload_length]
        cursor = payload_start + payload_length
        if payload.startswith("~h~"):
            continue
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            messages.append(decoded)
    return messages


def _tradingview_interval(interval: str) -> str:
    normalized = interval.strip().lower()
    mapping = {
        "1m": "1",
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "1h": "60",
        "2h": "120",
        "4h": "240",
        "1d": "1D",
        "1wk": "1W",
        "1mo": "1M",
    }
    try:
        return mapping[normalized]
    except KeyError as exc:
        raise MarketDataUnavailableError(
            f"TradingView interval is not supported: {interval}"
        ) from exc


def _history_count(period: str, interval: str) -> int:
    normalized_period = period.strip().lower()
    normalized_interval = interval.strip().lower()
    daily_counts = {
        "1mo": 40,
        "3mo": 90,
        "6mo": 180,
        "1y": 300,
        "2y": 550,
        "5y": 1400,
        "10y": 2800,
        "max": 5000,
    }
    if normalized_interval == "1d":
        return daily_counts.get(normalized_period, 300)
    intraday_counts = {
        "1d": 200,
        "5d": 500,
        "1mo": 1000,
        "3mo": 2000,
        "6mo": 4000,
    }
    return intraday_counts.get(normalized_period, 1000)


def _fingerprint_candles(candles: list[dict[str, object]]) -> str:
    canonical = json.dumps(
        candles,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _normalize_points(points: list[dict[str, Any]]) -> list[dict[str, object]]:
    candles_by_timestamp: dict[int, dict[str, object]] = {}
    for point in points:
        values = point.get("v")
        if not isinstance(values, list) or len(values) < 5:
            continue
        try:
            timestamp = int(float(values[0]))
            open_price = float(values[1])
            high_price = float(values[2])
            low_price = float(values[3])
            close_price = float(values[4])
            volume = float(values[5]) if len(values) > 5 and values[5] is not None else 0.0
        except (TypeError, ValueError):
            continue
        if min(open_price, high_price, low_price, close_price) <= 0:
            continue
        if high_price < max(open_price, low_price, close_price):
            continue
        if low_price > min(open_price, high_price, close_price):
            continue
        candles_by_timestamp[timestamp] = {
            "timestamp": datetime.fromtimestamp(timestamp, tz=UTC).isoformat(),
            "open": round(open_price, 6),
            "high": round(high_price, 6),
            "low": round(low_price, 6),
            "close": round(close_price, 6),
            "volume": round(max(volume, 0.0), 2),
        }
    return [candles_by_timestamp[key] for key in sorted(candles_by_timestamp)]


class TradingViewWebSocketClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.url = settings.tradingview_websocket_url
        self.origin = settings.tradingview_origin
        self.user_agent = settings.tradingview_user_agent
        self.auth_token = settings.tradingview_auth_token
        self.timeout_seconds = settings.market_data_timeout_seconds

    async def _connect(self) -> ClientConnection:
        return await websockets.connect(
            self.url,
            origin=self.origin,
            additional_headers={"User-Agent": self.user_agent},
            open_timeout=self.timeout_seconds,
            close_timeout=5,
            ping_interval=20,
            ping_timeout=20,
        )

    async def get_history(
        self,
        symbol: str,
        *,
        interval: str,
        count: int,
    ) -> list[dict[str, object]]:
        chart_session = _session_id("cs_")
        series_name = "s1"
        resolved_symbol = json.dumps(
            {"symbol": symbol, "adjustment": "splits"},
            separators=(",", ":"),
        )
        latest_points: list[dict[str, Any]] = []

        try:
            websocket = await self._connect()
            async with websocket:
                await websocket.send(
                    _frame_message("set_auth_token", [self.auth_token])
                )
                await websocket.send(
                    _frame_message("chart_create_session", [chart_session, ""])
                )
                await websocket.send(
                    _frame_message(
                        "resolve_symbol",
                        [chart_session, "symbol_1", f"={resolved_symbol}"],
                    )
                )
                await websocket.send(
                    _frame_message(
                        "create_series",
                        [
                            chart_session,
                            series_name,
                            series_name,
                            "symbol_1",
                            interval,
                            count,
                        ],
                    )
                )

                async with asyncio.timeout(self.timeout_seconds):
                    async for raw_message in websocket:
                        raw = raw_message.decode() if isinstance(raw_message, bytes) else raw_message
                        if "~h~" in raw and not raw.startswith("~m~"):
                            await websocket.send(raw)
                            continue
                        for message in _parse_messages(raw):
                            method = message.get("m")
                            params = message.get("p")
                            if method == "protocol_error":
                                raise MarketDataUnavailableError(
                                    f"TradingView protocol error for {symbol}: {params}"
                                )
                            if method == "critical_error":
                                raise MarketDataUnavailableError(
                                    f"TradingView critical error for {symbol}: {params}"
                                )
                            if method == "timescale_update" and isinstance(params, list):
                                if len(params) < 2 or params[0] != chart_session:
                                    continue
                                series_map = params[1]
                                if not isinstance(series_map, dict):
                                    continue
                                series = series_map.get(series_name)
                                if not isinstance(series, dict):
                                    continue
                                points = series.get("s")
                                if isinstance(points, list):
                                    latest_points = points
                            if method == "series_completed" and latest_points:
                                candles = _normalize_points(latest_points)
                                if candles:
                                    return candles
        except TimeoutError as exc:
            raise MarketDataUnavailableError(
                f"TradingView timed out for {symbol}"
            ) from exc
        except MarketDataUnavailableError:
            raise
        except Exception as exc:
            raise MarketDataUnavailableError(
                f"TradingView websocket failed for {symbol}"
            ) from exc

        candles = _normalize_points(latest_points)
        if not candles:
            raise MarketDataUnavailableError(
                f"TradingView returned no usable candles for {symbol}"
            )
        return candles


class TradingViewMarketDataProvider:
    name = "tradingview"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        normalized_ticker = normalize_egx_ticker(ticker)
        provider_symbol = f"EGX:{normalized_ticker}"
        tradingview_interval = _tradingview_interval(interval)
        count = _history_count(period, interval)
        client = TradingViewWebSocketClient()
        candles = await client.get_history(
            provider_symbol,
            interval=tradingview_interval,
            count=count,
        )
        fetched_at = datetime.now(UTC)
        data_as_of = datetime.fromisoformat(str(candles[-1]["timestamp"]))
        logger.info(
            "TradingView returned %s candles for %s through %s",
            len(candles),
            normalized_ticker,
            data_as_of.isoformat(),
        )
        return CandleSeries(
            ticker=normalized_ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=fetched_at,
            data_as_of=data_as_of,
            fingerprint=_fingerprint_candles(candles),
            candles=tuple(candles),
        )
