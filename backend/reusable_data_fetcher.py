from __future__ import annotations

import asyncio
import json
import logging
import random
import string
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import websockets
import yfinance as yf
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import ADXIndicator, EMAIndicator, MACD, SMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import MFIIndicator, VolumeWeightedAveragePrice

logger = logging.getLogger(__name__)

TRADINGVIEW_URL = "wss://data.tradingview.com/socket.io/websocket"
TRADINGVIEW_HEADERS = {
    "Origin": "https://www.tradingview.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36"
    ),
}
MARKET_MAP = {
    "EGX": {"tv_prefix": "EGX", "yf_suffix": ".CA"},
    "CASE": {"tv_prefix": "EGX", "yf_suffix": ".CA"},
    "US": {"tv_prefix": "NASDAQ", "yf_suffix": ""},
    "NASDAQ": {"tv_prefix": "NASDAQ", "yf_suffix": ""},
    "NYSE": {"tv_prefix": "NYSE", "yf_suffix": ""},
    "LSE": {"tv_prefix": "LSE", "yf_suffix": ".L"},
}


def _session_id(prefix: str = "") -> str:
    suffix = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=12)
    )
    return f"{prefix}{suffix}"


def _frame(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, separators=(",", ":"))
    return f"~m~{len(encoded)}~m~{encoded}"


def _parse_frames(raw: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    parts = raw.split("~m~")
    for index in range(2, len(parts), 2):
        try:
            decoded = json.loads(parts[index])
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(decoded, dict):
            messages.append(decoded)
    return messages


def _parse_symbol(symbol: str, market: str = "EGX") -> tuple[str, str]:
    cleaned = symbol.strip().upper()
    if ":" in cleaned:
        exchange, ticker = cleaned.split(":", 1)
        return exchange, ticker
    return market.strip().upper(), cleaned


def _tv_symbol(symbol: str, market: str = "EGX") -> str:
    exchange, ticker = _parse_symbol(symbol, market)
    config = MARKET_MAP.get(exchange, {"tv_prefix": exchange, "yf_suffix": ""})
    return f"{config['tv_prefix']}:{ticker}"


def _yf_symbol(symbol: str, market: str = "EGX") -> str:
    exchange, ticker = _parse_symbol(symbol, market)
    config = MARKET_MAP.get(exchange, {"tv_prefix": exchange, "yf_suffix": ""})
    return f"{ticker}{config['yf_suffix']}"


class TradingViewConnector:
    """Persistent WebSocket connector migrated from EGX-Pilot."""

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
        self._pending_history: dict[str, asyncio.Future[list[dict[str, Any]]]] = {}
        self._listener_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        if self.is_running and self.ws is not None:
            return
        self.ws = await websockets.connect(
            TRADINGVIEW_URL,
            origin=TRADINGVIEW_HEADERS["Origin"],
            additional_headers={
                "User-Agent": TRADINGVIEW_HEADERS["User-Agent"]
            },
            open_timeout=self.timeout_seconds,
            close_timeout=5,
            ping_interval=20,
            ping_timeout=20,
        )
        self.is_running = True
        await self.ws.send(
            _frame({"m": "set_auth_token", "p": [self.auth_token]})
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
                if raw.startswith("~h~"):
                    await self.ws.send(raw)
                    continue
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
        for future in [
            *self._pending_quotes.values(),
            *self._pending_history.values(),
        ]:
            if not future.done():
                future.set_exception(RuntimeError(reason))
        self._pending_quotes.clear()
        self._pending_history.clear()

    async def _dispatch(self, message: dict[str, Any]) -> None:
        method = message.get("m")
        params = message.get("p")
        if method == "qsd" and isinstance(params, list) and len(params) >= 2:
            quote = params[1]
            if not isinstance(quote, dict):
                return
            symbol = str(quote.get("n", ""))
            future = self._pending_quotes.pop(symbol, None)
            if future is None or future.done():
                return
            if quote.get("s") == "error":
                future.set_exception(
                    RuntimeError(str(quote.get("errmsg", "TradingView quote error")))
                )
            else:
                values = quote.get("v", {})
                future.set_result(values if isinstance(values, dict) else {})
            return

        if method == "timescale_update" and isinstance(params, list):
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
                future = self._pending_history.pop(request_id, None)
                if future is None or future.done():
                    continue
                candles: list[dict[str, Any]] = []
                for point in points:
                    values = point.get("v") if isinstance(point, dict) else None
                    if not isinstance(values, list) or len(values) < 5:
                        continue
                    candles.append(
                        {
                            "timestamp": values[0],
                            "open": values[1],
                            "high": values[2],
                            "low": values[3],
                            "close": values[4],
                            "volume": values[5] if len(values) > 5 else 0,
                        }
                    )
                future.set_result(candles)

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
            _frame({"m": "quote_create_session", "p": [session]})
        )
        await self.ws.send(
            _frame(
                {
                    "m": "quote_set_fields",
                    "p": [
                        session,
                        "lp",
                        "ch",
                        "chp",
                        "v",
                        "bid",
                        "ask",
                        "open_price",
                    ],
                }
            )
        )
        await self.ws.send(
            _frame({"m": "quote_add_symbols", "p": [session, symbol]})
        )
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
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
            _frame(
                {
                    "m": "chart_create_session",
                    "p": [chart_session, ""],
                }
            )
        )
        resolved = json.dumps(
            {"symbol": symbol, "adjustment": "splits"},
            separators=(",", ":"),
        )
        await self.ws.send(
            _frame(
                {
                    "m": "resolve_symbol",
                    "p": [chart_session, "symbol_1", f"={resolved}"],
                }
            )
        )
        await self.ws.send(
            _frame(
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
        auth_token: str = "unauthorized_user_token",
    ) -> None:
        self.size = size
        self.auth_token = auth_token
        self._connectors: list[TradingViewConnector] = []
        self._in_use: list[bool] = []
        self._condition = asyncio.Condition()

    async def acquire(self) -> TradingViewConnector:
        async with self._condition:
            while True:
                for index, connector in enumerate(self._connectors):
                    if not self._in_use[index]:
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
    @staticmethod
    def get_fundamentals(
        symbol: str,
        market: str = "EGX",
    ) -> dict[str, Any]:
        yahoo_symbol = _yf_symbol(symbol, market)
        empty = {
            "company_name": _parse_symbol(symbol, market)[1],
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
            value = info.get(key)
            return float(value) * 100 if value is not None else None

        return {
            **empty,
            "company_name": info.get("longName") or empty["company_name"],
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": percentage("dividendYield"),
            "beta": info.get("beta"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "volume_avg": info.get("averageVolume"),
            "revenue_growth": percentage("revenueGrowth"),
            "free_cash_flow": info.get("freeCashflow"),
            "eps_growth": percentage("earningsGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe": percentage("returnOnEquity"),
            "net_profit_margin": percentage("profitMargins"),
        }


class TechnicalAnalysisService:
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

        stochastic = StochasticOscillator(
            high,
            low,
            close,
            window=14,
            smooth_window=3,
        )
        frame["stoch_k"] = stochastic.stoch()
        frame["stoch_d"] = stochastic.stoch_signal()

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

        def number(column: str) -> float | None:
            value = latest.get(column)
            if value is None or pd.isna(value):
                return None
            return round(float(value), 6)

        sma_20 = number("sma_20")
        sma_50 = number("sma_50")
        sma_200 = number("sma_200")
        trend = "SIDEWAYS"
        if sma_50 is not None and sma_200 is not None:
            current = float(latest["close"])
            if current > sma_50 > sma_200:
                trend = "UPTREND"
            elif current < sma_50 < sma_200:
                trend = "DOWNTREND"

        return {
            "price": round(float(latest["close"]), 6),
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "ema_12": number("ema_12"),
            "ema_26": number("ema_26"),
            "rsi": number("rsi"),
            "macd": number("macd"),
            "macd_signal": number("macd_signal"),
            "macd_histogram": number("macd_histogram"),
            "stoch_k": number("stoch_k"),
            "stoch_d": number("stoch_d"),
            "bb_upper": number("bb_upper"),
            "bb_middle": number("bb_middle"),
            "bb_lower": number("bb_lower"),
            "atr": number("atr"),
            "adx": number("adx"),
            "di_plus": number("di_plus"),
            "di_minus": number("di_minus"),
            "vwap": number("vwap"),
            "mfi": number("mfi"),
            "trend": trend,
        }


@dataclass(slots=True)
class StockDataFetcher:
    tv_token: str = "unauthorized_user_token"
    pool_size: int = 3

    def __post_init__(self) -> None:
        self._pool = _ConnectionPool(
            size=self.pool_size,
            auth_token=self.tv_token,
        )
        self._fundamentals = FundamentalsFetcher()
        self._technical = TechnicalAnalysisService()

    async def get_realtime_price(
        self,
        symbol: str,
        market: str = "EGX",
    ) -> dict[str, Any]:
        formatted = _tv_symbol(symbol, market)
        connector = await self._pool.acquire()
        try:
            values = await connector.get_quote(formatted)
            return {
                "symbol": _parse_symbol(symbol, market)[1],
                "market": _parse_symbol(symbol, market)[0],
                "provider_symbol": formatted,
                "price": values.get("lp"),
                "change": values.get("ch"),
                "change_percent": values.get("chp"),
                "volume": values.get("v"),
                "bid": values.get("bid"),
                "ask": values.get("ask"),
                "open": values.get("open_price"),
            }
        finally:
            await self._pool.release(connector)

    async def get_historical_data(
        self,
        symbol: str,
        market: str = "EGX",
        timeframe: str = "1D",
        count: int = 200,
    ) -> list[dict[str, Any]]:
        if count < 1 or count > 5000:
            raise ValueError("count must be between 1 and 5000")
        formatted = _tv_symbol(symbol, market)
        connector = await self._pool.acquire()
        try:
            candles = await connector.get_historical(
                formatted,
                timeframe=timeframe,
                count=count,
            )
        finally:
            await self._pool.release(connector)
        return sorted(candles, key=lambda candle: float(candle["timestamp"]))

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
            asyncio.to_thread(self.get_fundamentals, ticker, exchange)
        )

        realtime_result, historical_result, fundamentals_result = (
            await asyncio.gather(
                realtime_task,
                historical_task,
                fundamentals_task,
                return_exceptions=True,
            )
        )
        if isinstance(historical_result, BaseException):
            raise historical_result
        historical = historical_result
        indicators = self.calculate_indicators(historical)

        if isinstance(realtime_result, BaseException):
            logger.warning(
                "Realtime quote failed for %s:%s: %s",
                exchange,
                ticker,
                realtime_result,
            )
            last = historical[-1] if historical else {}
            price = {
                "symbol": ticker,
                "market": exchange,
                "provider_symbol": _tv_symbol(ticker, exchange),
                "price": last.get("close"),
                "change": None,
                "change_percent": None,
                "volume": last.get("volume"),
                "bid": None,
                "ask": None,
                "open": last.get("open"),
                "source": "historical_fallback",
            }
        else:
            price = realtime_result
            price["source"] = "tradingview_realtime"

        fundamentals = (
            {"company_name": ticker}
            if isinstance(fundamentals_result, BaseException)
            else fundamentals_result
        )
        return {
            "symbol": ticker,
            "market": exchange,
            "price": price,
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
