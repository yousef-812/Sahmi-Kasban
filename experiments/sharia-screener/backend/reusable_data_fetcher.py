"""
Stock Data Fetcher - Reusable Module
=====================================
جلب بيانات أسهم من TradingView (WebSocket) + Yahoo Finance (أساسيات).
الموديول مستقل ولا يعتمد على قاعدة بيانات أو Framework معين.

المتطلبات:
    pip install websockets yfinance pandas numpy ta

الاستخدام:
    from reusable_data_fetcher import StockDataFetcher

    fetcher = StockDataFetcher()
    data = await fetcher.get_full_data("COMI", market="EGX")
    # data = {"ticker", "market", "price", "historical", "indicators", "fundamentals"}
"""

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
from ta.trend import MACD, ADXIndicator, CCIIndicator, EMAIndicator, SMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import MFIIndicator, VolumeWeightedAveragePrice

logger = logging.getLogger(__name__)

EXCHANGE_MAP: dict[str, dict[str, str]] = {
    "EGX": {"tv_prefix": "EGX", "yf_suffix": ".CA"},
    "CASE": {"tv_prefix": "EGX", "yf_suffix": ".CA"},
    "US": {"tv_prefix": "NASDAQ", "yf_suffix": ""},
    "NASDAQ": {"tv_prefix": "NASDAQ", "yf_suffix": ""},
    "NYSE": {"tv_prefix": "NYSE", "yf_suffix": ""},
    "LSE": {"tv_prefix": "LON", "yf_suffix": ".L"},
    "TADAWUL": {"tv_prefix": "TADAWUL", "yf_suffix": ".SR"},
    "DFM": {"tv_prefix": "DFM", "yf_suffix": ".DXB"},
    "ADX": {"tv_prefix": "ADX", "yf_suffix": ".AD"},
    "QSE": {"tv_prefix": "QSE", "yf_suffix": ".QA"},
    "BIST": {"tv_prefix": "BIST", "yf_suffix": ".IS"},
}
DEFAULT_EXCHANGE = "EGX"


def parse_symbol(symbol: str, market: str = DEFAULT_EXCHANGE) -> tuple[str, str]:
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise ValueError("symbol must not be empty")
    if ":" in cleaned:
        exchange, raw = cleaned.split(":", 1)
        if not exchange or not raw:
            raise ValueError(f"invalid symbol: {symbol}")
        return exchange, raw
    return market.strip().upper() or DEFAULT_EXCHANGE, cleaned


def get_tv_symbol(symbol: str, market: str = DEFAULT_EXCHANGE) -> str:
    exchange, raw = parse_symbol(symbol, market)
    config = EXCHANGE_MAP.get(exchange, {"tv_prefix": exchange, "yf_suffix": ""})
    return f"{config['tv_prefix']}:{raw}"


def get_yf_symbol(symbol: str, market: str = DEFAULT_EXCHANGE) -> str:
    exchange, raw = parse_symbol(symbol, market)
    config = EXCHANGE_MAP.get(exchange, {"tv_prefix": exchange, "yf_suffix": ""})
    return f"{raw}{config['yf_suffix']}"


def _sid(prefix: str = "") -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{prefix}{suffix}"


_HEARTBEAT_PATTERN = re.compile(r"~m~\d+~m~~h~\d+")


class TradingViewConnector:
    """Persistent TradingView WebSocket connector."""

    URL = "wss://data.tradingview.com/socket.io/websocket"
    HEADERS = {
        "Origin": "https://www.tradingview.com",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
    }

    def __init__(
        self,
        auth_token: str = "unauthorized_user_token",
        timeout_seconds: float = 20.0,
    ) -> None:
        self.auth_token = auth_token
        self.timeout_seconds = timeout_seconds
        self.ws: Any | None = None
        self.is_running = False
        self._lock = asyncio.Lock()
        self._pending_quotes: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._pending_historical: dict[str, asyncio.Future[list[dict[str, Any]]]] = {}
        self._listen_task: asyncio.Task[None] | None = None

    @staticmethod
    def _fmt(payload: Any) -> str:
        encoded = json.dumps(payload, separators=(",", ":"))
        return f"~m~{len(encoded)}~m~{encoded}"

    @staticmethod
    def _parse(data: str) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        cursor = 0
        marker = "~m~"
        while True:
            start = data.find(marker, cursor)
            if start < 0:
                break
            length_start = start + len(marker)
            length_end = data.find(marker, length_start)
            if length_end < 0:
                break
            try:
                payload_length = int(data[length_start:length_end])
            except ValueError:
                cursor = length_end + len(marker)
                continue
            payload_start = length_end + len(marker)
            payload = data[payload_start : payload_start + payload_length]
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

    async def connect(self) -> None:
        if self.is_running and self.ws is not None:
            return
        self.ws = await websockets.connect(
            self.URL,
            origin=self.HEADERS["Origin"],
            additional_headers={"User-Agent": self.HEADERS["User-Agent"]},
            open_timeout=self.timeout_seconds,
            close_timeout=5,
            ping_interval=20,
            ping_timeout=20,
        )
        self.is_running = True
        await self.ws.send(self._fmt({"m": "set_auth_token", "p": [self.auth_token]}))
        self._listen_task = asyncio.create_task(self._listen_loop())

    async def _listen_loop(self) -> None:
        try:
            async for raw_message in self.ws:
                raw = raw_message.decode() if isinstance(raw_message, bytes) else raw_message
                if raw.startswith("~h~"):
                    await self.ws.send(raw)
                    continue
                heartbeat = _HEARTBEAT_PATTERN.search(raw)
                if heartbeat is not None:
                    await self.ws.send(heartbeat.group(0))
                for message in self._parse(raw):
                    await self._dispatch(message)
        except asyncio.CancelledError:
            raise
        except websockets.ConnectionClosed:
            logger.warning("TradingView WebSocket connection closed")
        except Exception as exc:
            logger.warning("TradingView listener error: %s", exc)
        finally:
            self.is_running = False
            self._fail_pending("TradingView connection lost")

    def _fail_pending(self, reason: str) -> None:
        futures = [*self._pending_quotes.values(), *self._pending_historical.values()]
        for future in futures:
            if not future.done():
                future.set_exception(RuntimeError(reason))
        self._pending_quotes.clear()
        self._pending_historical.clear()

    async def _dispatch(self, message: dict[str, Any]) -> None:
        method = message.get("m")
        params = message.get("p")
        if method == "qsd" and isinstance(params, list) and len(params) >= 2:
            payload = params[1]
            if not isinstance(payload, dict):
                return
            symbol = str(payload.get("n", ""))
            async with self._lock:
                future = self._pending_quotes.pop(symbol, None)
            if future is None or future.done():
                return
            if payload.get("s") == "error":
                future.set_exception(RuntimeError(str(payload.get("errmsg", "TradingView quote error"))))
            else:
                values = payload.get("v", {})
                future.set_result(values if isinstance(values, dict) else {})
            return

        if method == "timescale_update" and isinstance(params, list) and len(params) >= 2:
            chart_session = str(params[0])
            series_map = params[1]
            if not isinstance(series_map, dict):
                return
            for series_name, series_data in series_map.items():
                if not isinstance(series_data, dict):
                    continue
                points = series_data.get("s")
                if not isinstance(points, list):
                    continue
                request_id = f"{chart_session}_{series_name}"
                async with self._lock:
                    future = self._pending_historical.pop(request_id, None)
                if future is not None and not future.done():
                    future.set_result(self._normalize_history(points))
            return

        if method in {"series_error", "protocol_error", "critical_error"}:
            reason = f"TradingView {method}: {params}"
            self._fail_pending(reason)

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
                volume = float(values[5]) if len(values) > 5 and values[5] is not None else 0.0
            except (TypeError, ValueError):
                continue
            if not all(np.isfinite(v) for v in (open_price, high_price, low_price, close_price, volume)):
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
        return [candles_by_timestamp[key] for key in sorted(candles_by_timestamp)]

    async def subscribe(self, symbols: list[str], session: str | None = None) -> str:
        await self.connect()
        session = session or _sid("qs_")
        await self.ws.send(self._fmt({"m": "quote_create_session", "p": [session]}))
        await self.ws.send(
            self._fmt(
                {
                    "m": "quote_set_fields",
                    "p": [session, "lp", "ch", "chp", "v", "bid", "ask", "open_price"],
                }
            )
        )
        for symbol in symbols:
            await self.ws.send(self._fmt({"m": "quote_add_symbols", "p": [session, symbol]}))
        return session

    async def get_quote(self, symbol: str, timeout: float = 10.0) -> dict[str, Any]:
        await self.connect()
        symbols_to_try = [symbol]
        if ":" in symbol:
            symbols_to_try.append(symbol.split(":", 1)[1])
        last_error: Exception | None = None
        for candidate in symbols_to_try:
            future = asyncio.get_running_loop().create_future()
            async with self._lock:
                self._pending_quotes[candidate] = future
            await self.subscribe([candidate])
            try:
                return await asyncio.wait_for(future, timeout=timeout)
            except RuntimeError as exc:
                last_error = exc
            finally:
                async with self._lock:
                    self._pending_quotes.pop(candidate, None)
        raise last_error or RuntimeError(f"No quote data for {symbol}")

    async def get_historical(
        self,
        symbol: str,
        timeframe: str = "1D",
        count: int = 200,
        timeout: float = 15.0,
    ) -> list[dict[str, Any]]:
        await self.connect()
        if not 1 <= count <= 5000:
            raise ValueError("count must be between 1 and 5000")
        chart_session = _sid("cs_")
        series_name = "s1"
        request_id = f"{chart_session}_{series_name}"
        future = asyncio.get_running_loop().create_future()
        async with self._lock:
            self._pending_historical[request_id] = future
        await self.ws.send(self._fmt({"m": "chart_create_session", "p": [chart_session, ""]}))
        resolved = json.dumps({"symbol": symbol, "adjustment": "splits"}, separators=(",", ":"))
        await self.ws.send(
            self._fmt(
                {
                    "m": "resolve_symbol",
                    "p": [chart_session, "symbol_1", f"={resolved}"],
                }
            )
        )
        await self.ws.send(
            self._fmt(
                {
                    "m": "create_series",
                    "p": [
                        chart_session,
                        series_name,
                        series_name,
                        "symbol_1",
                        timeframe,
                        count,
                    ],
                }
            )
        )
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            async with self._lock:
                self._pending_historical.pop(request_id, None)

    async def close(self) -> None:
        self.is_running = False
        if self._listen_task is not None:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None
        if self.ws is not None:
            await self.ws.close()
            self.ws = None
        self._fail_pending("TradingView connector closed")


class _ConnectionPool:
    def __init__(
        self,
        size: int = 2,
        auth_token: str = "unauthorized_user_token",
        timeout_seconds: float = 20.0,
    ) -> None:
        if size < 1:
            raise ValueError("pool size must be positive")
        self.size = size
        self.auth_token = auth_token
        self.timeout_seconds = timeout_seconds
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
                    connector = TradingViewConnector(
                        auth_token=self.auth_token,
                        timeout_seconds=self.timeout_seconds,
                    )
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


_default_pool: _ConnectionPool | None = None
_default_pool_lock = asyncio.Lock()


async def _get_pool() -> _ConnectionPool:
    global _default_pool
    async with _default_pool_lock:
        if _default_pool is None:
            _default_pool = _ConnectionPool(size=2)
        return _default_pool


class FundamentalsFetcher:
    @staticmethod
    def fetch(symbol: str, market: str = "EGX") -> dict[str, Any]:
        yahoo_symbol = get_yf_symbol(symbol, market)
        _, ticker = parse_symbol(symbol, market)
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
            "roe": None,
            "profit_margin": None,
            "debt_to_equity": None,
        }
        try:
            info = yf.Ticker(yahoo_symbol).info
        except Exception as exc:
            logger.warning("Fundamentals fetch failed for %s: %s", yahoo_symbol, exc)
            return empty

        def number(key: str) -> float | None:
            value = info.get(key)
            if value is None:
                return None
            try:
                parsed = float(value)
            except (TypeError, ValueError):
                return None
            return parsed if np.isfinite(parsed) else None

        def percentage(key: str) -> float | None:
            value = number(key)
            return value * 100 if value is not None else None

        return {
            **empty,
            "company_name": info.get("longName") or ticker,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": number("marketCap"),
            "pe_ratio": number("trailingPE"),
            "forward_pe": number("forwardPE"),
            "eps": number("trailingEps"),
            "dividend_yield": percentage("dividendYield"),
            "beta": number("beta"),
            "52w_high": number("fiftyTwoWeekHigh"),
            "52w_low": number("fiftyTwoWeekLow"),
            "volume_avg": number("averageVolume"),
            "revenue_growth": percentage("revenueGrowth"),
            "roe": percentage("returnOnEquity"),
            "profit_margin": percentage("profitMargins"),
            "debt_to_equity": number("debtToEquity"),
        }


class TechnicalAnalysisService:
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        if any(column not in df.columns for column in required):
            raise ValueError(f"OHLCV data must contain: {', '.join(required)}")
        frame = df.copy().sort_values("timestamp").drop_duplicates("timestamp", keep="last")
        for column in ["open", "high", "low", "close", "volume"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["open", "high", "low", "close"])
        frame["volume"] = frame["volume"].fillna(0).clip(lower=0)
        if len(frame) < 20:
            raise ValueError("at least 20 candles are required for indicators")

        close, high, low, volume = frame["close"], frame["high"], frame["low"], frame["volume"]
        frame["sma_20"] = SMAIndicator(close, window=20).sma_indicator()
        frame["sma_50"] = SMAIndicator(close, window=50).sma_indicator()
        frame["sma_200"] = SMAIndicator(close, window=200).sma_indicator()
        frame["ema_12"] = EMAIndicator(close, window=12).ema_indicator()
        frame["ema_26"] = EMAIndicator(close, window=26).ema_indicator()
        frame["rsi"] = RSIIndicator(close, window=14).rsi()
        macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        frame["macd"] = macd.macd()
        frame["macd_signal"] = macd.macd_signal()
        frame["macd_histogram"] = macd.macd_diff()
        stochastic = StochasticOscillator(high, low, close, window=14, smooth_window=3)
        frame["stoch_k"] = stochastic.stoch()
        frame["stoch_d"] = stochastic.stoch_signal()
        frame["cci"] = CCIIndicator(high, low, close, window=20).cci()
        frame["williams_r"] = WilliamsRIndicator(high, low, close, lbp=14).williams_r()
        frame["roc"] = ROCIndicator(close, window=12).roc()
        bands = BollingerBands(close, window=20, window_dev=2)
        frame["bb_upper"] = bands.bollinger_hband()
        frame["bb_middle"] = bands.bollinger_mavg()
        frame["bb_lower"] = bands.bollinger_lband()
        frame["atr"] = AverageTrueRange(high, low, close, window=14).average_true_range()
        frame["vwap"] = VolumeWeightedAveragePrice(
            high, low, close, volume, window=14
        ).volume_weighted_average_price()
        frame["mfi"] = MFIIndicator(high, low, close, volume, window=14).money_flow_index()
        frame["adx"] = ADXIndicator(high, low, close, window=14).adx()

        last_high = float(high.iloc[-1])
        last_low = float(low.iloc[-1])
        last_close = float(close.iloc[-1])
        pivot = (last_high + last_low + last_close) / 3
        frame["pivot_point"] = pivot
        frame["resistance_1"] = (2 * pivot) - last_low
        frame["resistance_2"] = pivot + (last_high - last_low)
        frame["support_1"] = (2 * pivot) - last_high
        frame["support_2"] = pivot - (last_high - last_low)

        recent = frame.tail(min(100, len(frame)))
        recent_high = float(recent["high"].max())
        recent_low = float(recent["low"].min())
        difference = recent_high - recent_low
        frame["fib_level_236"] = recent_high - difference * 0.236
        frame["fib_level_382"] = recent_high - difference * 0.382
        frame["fib_level_500"] = recent_high - difference * 0.5
        frame["fib_level_618"] = recent_high - difference * 0.618
        return frame

    def get_current_indicators(self, df: pd.DataFrame) -> dict[str, Any]:
        latest = df.iloc[-1]

        def value(column: str) -> float | None:
            item = latest.get(column)
            if item is None or pd.isna(item):
                return None
            parsed = float(item)
            return parsed if np.isfinite(parsed) else None

        columns = [
            "rsi",
            "macd",
            "macd_signal",
            "macd_histogram",
            "sma_20",
            "sma_50",
            "sma_200",
            "ema_12",
            "ema_26",
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "atr",
            "adx",
            "stoch_k",
            "stoch_d",
            "cci",
            "williams_r",
            "roc",
            "mfi",
            "vwap",
            "pivot_point",
            "resistance_1",
            "resistance_2",
            "support_1",
            "support_2",
            "fib_level_236",
            "fib_level_382",
            "fib_level_500",
            "fib_level_618",
        ]
        result = {column: value(column) for column in columns}
        result["price"] = value("close")
        result["pivot"] = result.pop("pivot_point")
        result["fib_236"] = result.pop("fib_level_236")
        result["fib_382"] = result.pop("fib_level_382")
        result["fib_500"] = result.pop("fib_level_500")
        result["fib_618"] = result.pop("fib_level_618")
        return result


class StockDataFetcher:
    """Facade for realtime, historical, technical, and fundamental stock data."""

    def __init__(
        self,
        tv_token: str = "unauthorized_user_token",
        pool_size: int = 2,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.tv_token = tv_token
        self.ta = TechnicalAnalysisService()
        self._pool = _ConnectionPool(pool_size, tv_token, timeout_seconds)

    async def _fresh_connector(self) -> TradingViewConnector:
        connector = TradingViewConnector(auth_token=self.tv_token)
        await connector.connect()
        return connector

    async def get_realtime_price(
        self,
        symbol: str,
        market: str = "EGX",
    ) -> dict[str, Any]:
        exchange, ticker = parse_symbol(symbol, market)
        formatted = get_tv_symbol(ticker, exchange)
        connector = await self._pool.acquire()
        try:
            values = await connector.get_quote(formatted, timeout=10.0)
            return {
                "symbol": ticker,
                "market": exchange,
                "provider_symbol": formatted,
                "price": values.get("lp"),
                "change": values.get("ch"),
                "change_percent": values.get("chp"),
                "volume": values.get("v"),
                "bid": values.get("bid"),
                "ask": values.get("ask"),
                "open": values.get("open_price"),
                "source": "tradingview_realtime",
            }
        except Exception as exc:
            logger.warning("Realtime price failed for %s: %s", formatted, exc)
            return {"symbol": ticker, "market": exchange, "price": None, "source": "unavailable"}
        finally:
            await self._pool.release(connector)

    async def get_historical_data(
        self,
        symbol: str,
        market: str = "EGX",
        timeframe: str = "1D",
        count: int = 200,
    ) -> list[dict[str, Any]]:
        exchange, ticker = parse_symbol(symbol, market)
        formatted = get_tv_symbol(ticker, exchange)
        connector = await self._pool.acquire()
        try:
            return await connector.get_historical(formatted, timeframe, count, timeout=15.0)
        except Exception as exc:
            logger.warning("Historical data failed for %s: %s", formatted, exc)
            return []
        finally:
            await self._pool.release(connector)

    def get_fundamentals(self, symbol: str, market: str = "EGX") -> dict[str, Any]:
        return FundamentalsFetcher.fetch(symbol, market)

    def calculate_indicators(self, historical: list[dict[str, Any]]) -> dict[str, Any]:
        if not historical:
            return {}
        frame = pd.DataFrame(historical)
        try:
            calculated = self.ta.calculate_all_indicators(frame)
        except (ValueError, KeyError, TypeError) as exc:
            logger.warning("Indicator calculation failed: %s", exc)
            return {}
        return self.ta.get_current_indicators(calculated)

    async def get_full_data(
        self,
        symbol: str,
        market: str = "EGX",
        timeframe: str = "1D",
        count: int = 200,
        include_fundamentals: bool = True,
    ) -> dict[str, Any]:
        exchange, ticker = parse_symbol(symbol, market)
        price_task = asyncio.create_task(self.get_realtime_price(ticker, exchange))
        historical_task = asyncio.create_task(self.get_historical_data(ticker, exchange, timeframe, count))
        price, historical = await asyncio.gather(price_task, historical_task)

        errors: list[str] = []
        if not historical:
            errors.append("historical_data_unavailable")
        if price.get("price") is None and historical:
            latest = historical[-1]
            price = {
                "symbol": ticker,
                "market": exchange,
                "provider_symbol": get_tv_symbol(ticker, exchange),
                "price": latest.get("close"),
                "change": None,
                "change_percent": None,
                "volume": latest.get("volume"),
                "bid": None,
                "ask": None,
                "open": latest.get("open"),
                "source": "historical_fallback",
            }
        elif price.get("price") is None:
            errors.append("realtime_price_unavailable")

        indicators = self.calculate_indicators(historical)
        fundamentals: dict[str, Any] = {}
        if include_fundamentals:
            try:
                fundamentals = await asyncio.to_thread(
                    self.get_fundamentals,
                    ticker,
                    exchange,
                )
            except Exception as exc:
                logger.warning("Fundamentals failed for %s:%s: %s", exchange, ticker, exc)
                errors.append("fundamentals_unavailable")

        return {
            "ticker": ticker,
            "market": exchange,
            "price": price,
            "historical": historical,
            "indicators": indicators,
            "fundamentals": fundamentals,
            "errors": errors,
        }

    async def close(self) -> None:
        await self._pool.close()


__all__ = [
    "EXCHANGE_MAP",
    "FundamentalsFetcher",
    "StockDataFetcher",
    "TechnicalAnalysisService",
    "TradingViewConnector",
    "get_tv_symbol",
    "get_yf_symbol",
    "parse_symbol",
]
