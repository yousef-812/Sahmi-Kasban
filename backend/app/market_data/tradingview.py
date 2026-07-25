from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime

from reusable_data_fetcher import TradingViewConnector, get_tv_symbol

from app.core.config import get_settings
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.types import CandleSeries, MarketDataUnavailableError

logger = logging.getLogger(__name__)


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


def _normalize_candles(candles: list[dict[str, object]]) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for candle in candles:
        try:
            timestamp = int(candle["timestamp"])
            open_price = float(candle["open"])
            high_price = float(candle["high"])
            low_price = float(candle["low"])
            close_price = float(candle["close"])
            volume = float(candle.get("volume", 0))
        except (KeyError, TypeError, ValueError):
            continue
        normalized.append(
            {
                "timestamp": datetime.fromtimestamp(timestamp, tz=UTC).isoformat(),
                "open": round(open_price, 6),
                "high": round(high_price, 6),
                "low": round(low_price, 6),
                "close": round(close_price, 6),
                "volume": round(max(volume, 0.0), 2),
            }
        )
    return normalized


class TradingViewMarketDataProvider:
    name = "tradingview"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        settings = get_settings()
        normalized_ticker = normalize_egx_ticker(ticker)
        provider_symbol = get_tv_symbol(normalized_ticker, "EGX")
        tradingview_interval = _tradingview_interval(interval)
        count = _history_count(period, interval)

        connector = TradingViewConnector(
            auth_token=settings.tradingview_auth_token,
            timeout_seconds=settings.market_data_timeout_seconds,
        )
        connector.URL = settings.tradingview_websocket_url
        connector.HEADERS = {
            "Origin": settings.tradingview_origin,
            "User-Agent": settings.tradingview_user_agent,
        }
        try:
            raw_candles = await connector.get_historical(
                provider_symbol,
                timeframe=tradingview_interval,
                count=count,
                timeout=settings.market_data_timeout_seconds,
            )
        except Exception as exc:
            raise MarketDataUnavailableError(
                f"TradingView websocket failed for {provider_symbol}"
            ) from exc
        finally:
            await connector.close()

        candles = _normalize_candles(raw_candles)
        if len(candles) < settings.market_data_min_candles:
            raise MarketDataUnavailableError(
                "TradingView returned "
                f"{len(candles)} candles for {provider_symbol}; "
                f"at least {settings.market_data_min_candles} are required"
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
