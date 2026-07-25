from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import string
from typing import Any

import numpy as np
import pandas as pd
import websockets
import yfinance as yf
from ta.momentum import ROCIndicator, RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import ADXIndicator, CCIIndicator, EMAIndicator, MACD, SMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import MFIIndicator, VolumeWeightedAveragePrice

logger = logging.getLogger(__name__)

TRADINGVIEW_URL = "wss://data.tradingview.com/socket.io/websocket"
TRADINGVIEW_ORIGIN = "https://www.tradingview.com"
TRADINGVIEW_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36"
)
TRADINGVIEW_UNAUTHORIZED_TOKEN = "unauthorized_user_token"

MARKET_MAP: dict[str, dict[str, str]] = {
    "EGX": {"tv_prefix": "EGX", "yf_suffix": ".CA"},
    "CASE": {"tv_prefix": "EGX", "yf_suffix": ".CA"},
    "US": {"tv_prefix": "NASDAQ", "yf_suffix": ""},
    "NASDAQ": {"tv_prefix": "NASDAQ", "yf_suffix": ""},
    "NYSE": {"tv_prefix": "NYSE", "yf_suffix": ""},
    "LSE": {"tv_prefix": "LSE", "yf_suffix": ".L"},
}

_HEARTBEAT_PATTERN = re.compile(r"~m~\d+~m~~h~\d+")


def _session_id(prefix: str) -> str:
    suffix = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=12)
    )
    return f"{prefix}{suffix}"


def _frame(method: str, params: list[object]) -> str:
    payload = json.dumps(
        {"m": method, "p": params},
        separators=(",", ":"),
    )
    return f"~m~{len(payload)}~m~{payload}"


def _parse_frames(raw: str) -> list[dict[str, Any]]:
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
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            messages.append(decoded)
    return messages


def _parse_symbol(symbol: str, market: str = "EGX") -> tuple[str, str]:
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise ValueError("symbol must not be empty")
    if ":" in cleaned:
        exchange, ticker = cleaned.split(":", 1)
        return exchange, ticker
    return market.strip().upper(), cleaned


def _provider_symbols(symbol: str, market: str = "EGX") -> tuple[str, str]:
    exchange, ticker = _parse_symbol(symbol, market)
    config = MARKET_MAP.get(
        exchange,
        {"tv_prefix": exchange, "yf_suffix": ""},
    )
    return (
        f"{config['tv_prefix']}:{ticker}",
        f"{ticker}{config['yf_suffix']}",
    )


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if np.isfinite(parsed) else None


class TradingViewConnector:
    """Persistent TradingView WebSocket connector migrated from EGX-Pilot."""

    def __init__(
        self,
        auth_token: str = TRADINGVIEW_UNAUTHORIZED_TOKEN,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.auth_token = auth_token
        self.timeout_seconds = timeout_seconds
        self.ws: Any | None = None
        self.is_running = False
        self._lock = asyncio.Lock()
        self._pending_quotes: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._pending_history: dict[
            str,
            asyncio.Future[list[dict[str, Any]]],
        ] = {}
        self._listener_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        if self.is_running and self.ws is not None:
            return
        self.ws = await websockets.connect(
            TRADINGVIEW_URL,
            origin=TRADINGVIEW_ORIGIN,
            additional_headers={"User-Agent": TRADINGVIEW_USER_AGENT},
            open_timeout=self.timeout_seconds,
            close_timeout=5,
            ping_interval=20,
            ping_timeout=20,
        )
        self.is_running = True
        await self.ws.send(
            _frame("set_auth_token", [self.auth_token])
        )
        self._listener_task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        try:
            async for raw_message in self.ws:
                raw = (
                    raw_message.decode()
                    if isinstance(raw_message, bytes)
                    else raw_message
                )
                heartbeat = _HEARTBEAT_PATTERN.search(raw)
                if heartbeat is not None:
                    await self.ws.send(heartbeat.group(0))
                for message in _parse_frames(raw):
                    await self._dispatch(message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("TradingView listener stopped: %s", exc)
        finally:
            self.is_running = False
            self._fail_pending("TradingView connection closed")

    def _fail_pending(self, reason: str) -> None:
        futures = [
            *self._pending_quotes.values(),
            *self._pending_history.values(),
        ]
        for future in futures:
            if not future.done():
                future.set_exception(RuntimeError(reason))
        self._pending_quotes.clear()
        self._pending_history.clear()

    async def _dispatch(self, message: dict[str, Any]) -> None:
        method = message.get("m")
        params = message.get("p")
        if method == "qsd" and isinstance(params, list) and len(params) >= 2:
            await self._dispatch_quote(params[1])
            return
        if method == "timescale_update" and isinstance(params, list):
            await self._dispatch_history(params)

    async def _dispatch_quote(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        symbol = str(payload.get("n", ""))
        async with self._lock:
            future = self._pending_quotes.pop(symbol, None)
        if future is None or future.done():
            return
        if payload.get("s") == "error":
            message = str(payload.get("errmsg", "TradingView quote error"))
            future.set_exception(RuntimeError(message))
            return
        values = payload.get("v", {})
        future.set_result(values if isinstance(values, dict) else {})

    async def _dispatch_history(self, params: list[Any]) -> None:
        if len(params) < 2 or not isinstance(params[1], dict):
            return
        chart_session = str(params[0])
        for series_name, series_data in params[1].items():
            if not isinstance(series_data, dict):
                continue
            points = series_data.get("s")
            if not isinstance(points, list):
                continue
            request_id = f"{chart_session}_{series_name}"
            async with self._lock:
                future = self._pending_history.pop(request_id, None)
            if future is None or future.done():
                continue
            future.set_result(self._normalize_history(points))

    @staticmethod
    def _normalize_history(points: list[Any]) -> list[dict[str, Any]]:
        candles_by_timestamp: dict[int, dict[str, Any]] = {}
        for point in points:
            values = point.get("v") if isinstance(point, dict) else None
            if not isinstance(values, list) or len(values) < 5:
                continue
            try:
                timestamp = int(float(values[0]))
                open_price = float(values[1])
                high_price = float(values[2])
                low_price = float(values[3])
                close_price = float(values[4])
                volume = (
                    float(values[5])
                    if len(values) > 5 and values[5] is not None
                    else 0.0
                )
            except (TypeError, ValueError):
                continue
            if min(open_price, high_price, low_price, close_price) <= 0:
                continue
            if high_price < max(open_price, low_price, close_price):
                continue
            if low_price > min(open_price, high_price, close_price):
                continue
            candles_by_timestamp[timestamp] = {
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": max(volume, 0.0),
            }
        return [
            candles_by_timestamp[timestamp]
            for timestamp in sorted(candles_by_timestamp)
        ]

    async def get_quote(
        self,
        symbol: str,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        await self.connect()
        session = _session_id("qs_")
        future = asyncio.get_running_loop().create_future()
        async with self._lock:
            self._pending_quotes[symbol] = future
        await self.ws.send(
            _frame("quote_create_session", [session])
        )
        await self.ws.send(
            _frame(
                "quote_set_fields",
                [
                    session,
                    "lp",
                    "ch",
                    "chp",
                    "v",
                    "bid",
                    "ask",
                    "open_price",
                ],
            )
        )
        await self.ws.send(
            _frame("quote_add_symbols", [session, symbol])
        )
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            async with self._lock:
                self._pending_quotes.pop(symbol, None)

    async def get_historical(
        self,
        symbol: str,
        timeframe: str = "1D",
        count: int = 200,
        timeout: float = 20.0,
    ) -> list[dict[str, Any]]:
        await self.connect()
        chart_session = _session_id("cs_")
        series_name = "s1"
        request_id = f"{chart_session}_{series_name}"
        future = asyncio.get_running_loop().create_future()
        async with self._lock:
            self._pending_history[request_id] = future
        await self.ws.send(
            _frame("chart_create_session", [chart_session, ""])
        )
        resolved = json.dumps(
            {"symbol": symbol, "adjustment": "splits"},
            separators=(",", ":"),
        )
        await self.ws.send(
            _frame(
                "resolve_symbol",
                [chart_session, "symbol_1", f"={resolved}"],
            )
        )
        await self.ws.send(
            _frame(
                "create_series",
                [
                    chart_session,
                    series_name,
                    series_name,
                    "symbol_1",
                    timeframe,
                    count,
                ],
            )
        )
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            async with self._lock:
                self._pending_history.pop(request_id, None)

    async def close(self) -> None:
        self.is_running = False
        if self._listener_task is not None:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
        if self.ws is not None:
            await self.ws.close()
            self.ws = None
        self._fail_pending("TradingView connector closed")


class _ConnectionPool:
    def __init__(
        self,
        size: int = 3,
        auth_token: str = TRADINGVIEW_UNAUTHORIZED_TOKEN,
    ) -> None:
        if size < 1:
            raise ValueError("pool size must be positive")
        self.size = size
        self.auth_token = auth_token
        self._connectors: list[TradingViewConnector] = []
        self._in_use: list[bool] = []
        self._condition = asyncio.Condition()

    async def acquire(self) -> TradingViewConnector:
        async with self._condition:
            while True:
                for index, connector in enumerate(self._connectors):
                    if self._in_use[index]:
                        continue
                    if not connector.is_running:
                        await connector.connect()
                    self._in_use[index] = True
                    return connector
                if len(self._connectors) < self.size:
                    connector = TradingViewConnector(self.auth_token)
                    await connector.connect()
                    self._connectors.append(connector)
                    self._in_use.append(True)
                    return connector
                await self._condition.wait()

    async def release(self, connector: TradingViewConnector) -> None:
        async with self._condition:
            for index, item in enumerate(self._connectors):
                if item is connector:
                    self._in_use[index] = False
                    self._condition.notify(1)
                    return
        await connector.close()

    async def close(self) -> None:
        connectors = list(self._connectors)
        self._connectors.clear()
        self._in_use.clear()
        await asyncio.gather(
            *(connector.close() for connector in connectors),
            return_exceptions=True,
        )


class FundamentalsFetcher:
    """Fetches company fundamentals through Yahoo Finance."""

    @staticmethod
    def get_fundamentals(
        symbol: str,
        market: str = "EGX",
    ) -> dict[str, Any]:
        _, yahoo_symbol = _provider_symbols(symbol, market)
        _, ticker = _parse_symbol(symbol, market)
        empty: dict[str, Any] = {
            "company_name": ticker,
            "sector": None,
            "industry": None,
            "market_cap": None,
            "pe_ratio": None,
            "forward_pe": None,
            "eps": None,
            "dividend_yield": None,
            "beta": None,
            "52w_high": None,
            "52w_low": None,
            "volume_avg": None,
            "revenue_growth": None,
            "free_cash_flow": None,
            "eps_growth": None,
            "debt_to_equity": None,
            "roe": None,
            "net_profit_margin": None,
        }
        try:
            info = yf.Ticker(yahoo_symbol).info
        except Exception as exc:
            logger.warning("Fundamentals failed for %s: %s", yahoo_symbol, exc)
            return empty

        def percentage(key: str) -> float | None:
            value = _number(info.get(key))
            return value * 100 if value is not None else None

        return {
            **empty,
            "company_name": info.get("longName") or ticker,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": _number(info.get("marketCap")),
            "pe_ratio": _number(info.get("trailingPE")),
            "forward_pe": _number(info.get("forwardPE")),
            "eps": _number(info.get("trailingEps")),
            "dividend_yield": percentage("dividendYield"),
            "beta": _number(info.get("beta")),
            "52w_high": _number(info.get("fiftyTwoWeekHigh")),
            "52w_low": _number(info.get("fiftyTwoWeekLow")),
            "volume_avg": _number(info.get("averageVolume")),
            "revenue_growth": percentage("revenueGrowth"),
            "free_cash_flow": _number(info.get("freeCashflow")),
            "eps_growth": percentage("earningsGrowth"),
            "debt_to_equity": _number(info.get("debtToEquity")),
            "roe": percentage("returnOnEquity"),
            "net_profit_margin": percentage("profitMargins"),
        }


class TechnicalAnalysisService:
    """Calculates a compact set of technical indicators from OHLCV candles."""

    @staticmethod
    def calculate_indicators(
        candles: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not candles:
            return {}
        frame = pd.DataFrame(candles).copy()
        required = ["open", "high", "low", "close", "volume"]
        if any(column not in frame.columns for column in required):
            return {}
        for column in required:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["open", "high", "low", "close"])
        if len(frame) < 20:
            return {}
        frame["volume"] = frame["volume"].fillna(0).clip(lower=0)

        close = frame["close"]
        high = frame["high"]
        low = frame["low"]
        volume = frame["volume"]

        for window in (20, 50, 200):
            frame[f"sma_{window}"] = SMAIndicator(
                close,
                window=window,
                fillna=False,
            ).sma_indicator()
        for window in (9, 12, 21, 26):
            frame[f"ema_{window}"] = EMAIndicator(
                close,
                window=window,
                fillna=False,
            ).ema_indicator()

        frame["rsi"] = RSIIndicator(close, window=14).rsi()
        macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        frame["macd"] = macd.macd()
        frame["macd_signal"] = macd.macd_signal()
        frame["macd_histogram"] = macd.macd_diff()

        stochastic = StochasticOscillator(
            high,
            low,
            close,
            window=14,
            smooth_window=3,
        )
        frame["stoch_k"] = stochastic.stoch()
        frame["stoch_d"] = stochastic.stoch_signal()
        frame["williams_r"] = WilliamsRIndicator(
            high,
            low,
            close,
            lbp=14,
        ).williams_r()
        frame["roc"] = ROCIndicator(close, window=12).roc()
        frame["cci"] = CCIIndicator(
            high,
            low,
            close,
            window=20,
        ).cci()

        bands = BollingerBands(close, window=20, window_dev=2)
        frame["bb_upper"] = bands.bollinger_hband()
        frame["bb_middle"] = bands.bollinger_mavg()
        frame["bb_lower"] = bands.bollinger_lband()
        frame["atr"] = AverageTrueRange(
            high,
            low,
            close,
            window=14,
        ).average_true_range()

        adx = ADXIndicator(high, low, close, window=14)
        frame["adx"] = adx.adx()
        frame["di_plus"] = adx.adx_pos()
        frame["di_minus"] = adx.adx_neg()
        frame["vwap"] = VolumeWeightedAveragePrice(
            high,
            low,
            close,
            volume,
            window=14,
        ).volume_weighted_average_price()
        frame["mfi"] = MFIIndicator(
            high,
            low,
            close,
            volume,
            window=14,
        ).money_flow_index()

        latest = frame.iloc[-1]

        def latest_number(column: str) -> float | None:
            value = latest.get(column)
            parsed = _number(value)
            return round(parsed, 6) if parsed is not None else None

        sma_50 = latest_number("sma_50")
        sma_200 = latest_number("sma_200")
        current_price = float(latest["close"])
        trend = "SIDEWAYS"
        if sma_50 is not None and sma_200 is not None:
            if current_price > sma_50 > sma_200:
                trend = "UPTREND"
            elif current_price < sma_50 < sma_200:
                trend = "DOWNTREND"

        columns = (
            "sma_20",
            "sma_50",
            "sma_200",
            "ema_9",
            "ema_12",
            "ema_21",
            "ema_26",
            "rsi",
            "macd",
            "macd_signal",
            "macd_histogram",
            "stoch_k",
            "stoch_d",
            "williams_r",
            "roc",
            "cci",
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "atr",
            "adx",
            "di_plus",
            "di_minus",
            "vwap",
            "mfi",
        )
        result = {
            column: latest_number(column)
            for column in columns
        }
        result.update(
            {
                "price": round(current_price, 6),
                "trend": trend,
            }
        )
        return result


class StockDataFetcher:
    """Facade for realtime, historical, technical, and fundamental data."""

    def __init__(
        self,
        tv_token: str = TRADINGVIEW_UNAUTHORIZED_TOKEN,
        pool_size: int = 3,
    ) -> None:
        self.tv_token = tv_token
        self.pool_size = pool_size
        self._pool = _ConnectionPool(pool_size, tv_token)
        self._fundamentals = FundamentalsFetcher()
        self._technical = TechnicalAnalysisService()

    async def get_realtime_price(
        self,
        symbol: str,
        market: str = "EGX",
    ) -> dict[str, Any]:
        exchange, ticker = _parse_symbol(symbol, market)
        tradingview_symbol, _ = _provider_symbols(ticker, exchange)
        connector = await self._pool.acquire()
        try:
            values = await connector.get_quote(tradingview_symbol)
        finally:
            await self._pool.release(connector)
        return {
            "symbol": ticker,
            "market": exchange,
            "provider_symbol": tradingview_symbol,
            "price": _number(values.get("lp")),
            "change": _number(values.get("ch")),
            "change_percent": _number(values.get("chp")),
            "volume": _number(values.get("v")),
            "bid": _number(values.get("bid")),
            "ask": _number(values.get("ask")),
            "open": _number(values.get("open_price")),
            "source": "tradingview_realtime",
        }

    async def get_historical_data(
        self,
        symbol: str,
        market: str = "EGX",
        timeframe: str = "1D",
        count: int = 200,
    ) -> list[dict[str, Any]]:
        if not 1 <= count <= 5000:
            raise ValueError("count must be between 1 and 5000")
        exchange, ticker = _parse_symbol(symbol, market)
        tradingview_symbol, _ = _provider_symbols(ticker, exchange)
        connector = await self._pool.acquire()
        try:
            return await connector.get_historical(
                tradingview_symbol,
                timeframe=timeframe,
                count=count,
            )
        finally:
            await self._pool.release(connector)

    def get_fundamentals(
        self,
        symbol: str,
        market: str = "EGX",
    ) -> dict[str, Any]:
        return self._fundamentals.get_fundamentals(symbol, market)

    def calculate_indicators(
        self,
        candles: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._technical.calculate_indicators(candles)

    async def get_full_data(
        self,
        symbol: str,
        market: str = "EGX",
        timeframe: str = "1D",
        count: int = 200,
    ) -> dict[str, Any]:
        exchange, ticker = _parse_symbol(symbol, market)
        realtime_task = asyncio.create_task(
            self.get_realtime_price(ticker, exchange)
        )
        historical_task = asyncio.create_task(
            self.get_historical_data(
                ticker,
                exchange,
                timeframe=timeframe,
                count=count,
            )
        )
        fundamentals_task = asyncio.create_task(
            asyncio.to_thread(
                self.get_fundamentals,
                ticker,
                exchange,
            )
        )
        realtime, historical, fundamentals = await asyncio.gather(
            realtime_task,
            historical_task,
            fundamentals_task,
            return_exceptions=True,
        )
        if isinstance(historical, BaseException):
            raise historical
        if not historical:
            raise RuntimeError(
                f"TradingView returned no historical data for {exchange}:{ticker}"
            )

        indicators = self.calculate_indicators(historical)
        if isinstance(realtime, BaseException):
            logger.warning(
                "Realtime quote failed for %s:%s: %s",
                exchange,
                ticker,
                realtime,
            )
            last = historical[-1]
            realtime = {
                "symbol": ticker,
                "market": exchange,
                "provider_symbol": _provider_symbols(ticker, exchange)[0],
                "price": _number(last.get("close")),
                "change": None,
                "change_percent": None,
                "volume": _number(last.get("volume")),
                "bid": None,
                "ask": None,
                "open": _number(last.get("open")),
                "source": "historical_fallback",
            }
        if isinstance(fundamentals, BaseException):
            logger.warning(
                "Fundamentals failed for %s:%s: %s",
                exchange,
                ticker,
                fundamentals,
            )
            fundamentals = {"company_name": ticker}

        return {
            "symbol": ticker,
            "market": exchange,
            "price": realtime,
            "historical": historical,
            "indicators": indicators,
            "fundamentals": fundamentals,
        }

    async def close(self) -> None:
        await self._pool.close()


__all__ = [
    "FundamentalsFetcher",
    "StockDataFetcher",
    "TechnicalAnalysisService",
    "TradingViewConnector",
]
