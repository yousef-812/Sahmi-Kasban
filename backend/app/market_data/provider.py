from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import UTC, datetime
from functools import lru_cache

import pandas as pd
import yfinance as yf

from app.core.config import get_settings
from app.market_data.egx_symbols import normalize_egx_ticker, to_yahoo_symbol
from app.market_data.types import CandleSeries, MarketDataProvider, MarketDataUnavailableError

logger = logging.getLogger(__name__)


def _fingerprint_candles(candles: list[dict[str, object]]) -> str:
    canonical = json.dumps(candles, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class YFinanceMarketDataProvider:
    name = "yfinance"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        normalized_ticker = normalize_egx_ticker(ticker)
        settings = get_settings()

        def download() -> pd.DataFrame:
            provider_ticker = yf.Ticker(to_yahoo_symbol(normalized_ticker))
            return provider_ticker.history(
                period=period,
                interval=interval,
                auto_adjust=False,
                actions=False,
                repair=True,
                timeout=settings.market_data_timeout_seconds,
                raise_errors=True,
            )

        try:
            frame = await asyncio.to_thread(download)
        except Exception as exc:
            raise MarketDataUnavailableError(
                f"yfinance failed for {normalized_ticker}"
            ) from exc

        candles = self._normalize_frame(frame)
        if not candles:
            raise MarketDataUnavailableError(
                f"yfinance returned no usable candles for {normalized_ticker}"
            )

        fetched_at = datetime.now(UTC)
        data_as_of = datetime.fromisoformat(str(candles[-1]["timestamp"]))
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

    @staticmethod
    def _normalize_frame(frame: pd.DataFrame) -> list[dict[str, object]]:
        if frame is None or frame.empty:
            return []

        normalized = frame.copy()
        normalized.columns = [str(column).strip().lower().replace(" ", "_") for column in normalized.columns]
        required = ["open", "high", "low", "close", "volume"]
        if any(column not in normalized.columns for column in required):
            return []

        timestamps = pd.to_datetime(normalized.index, errors="coerce", utc=True)
        normalized = normalized.assign(timestamp=timestamps)
        for column in required:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
        normalized = normalized.dropna(subset=["timestamp", "open", "high", "low", "close"])
        normalized["volume"] = normalized["volume"].fillna(0).clip(lower=0)
        normalized = normalized.sort_values("timestamp").drop_duplicates("timestamp", keep="last")

        candles: list[dict[str, object]] = []
        for row in normalized.itertuples(index=False):
            open_price = float(row.open)
            high_price = float(row.high)
            low_price = float(row.low)
            close_price = float(row.close)
            if min(open_price, high_price, low_price, close_price) <= 0:
                continue
            if high_price < max(open_price, low_price, close_price):
                continue
            if low_price > min(open_price, high_price, close_price):
                continue
            candles.append(
                {
                    "timestamp": row.timestamp.to_pydatetime().isoformat(),
                    "open": round(open_price, 6),
                    "high": round(high_price, 6),
                    "low": round(low_price, 6),
                    "close": round(close_price, 6),
                    "volume": round(float(row.volume), 2),
                }
            )
        return candles


class FallbackMarketDataProvider:
    def __init__(self, providers: tuple[MarketDataProvider, ...]) -> None:
        if not providers:
            raise ValueError("At least one market-data provider is required")
        self.providers = providers
        self.name = "+".join(provider.name for provider in providers)

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        failures: list[str] = []
        for provider in self.providers:
            try:
                return await provider.get_history(ticker, period=period, interval=interval)
            except MarketDataUnavailableError as exc:
                failures.append(f"{provider.name}: {exc}")
                logger.warning("Market data provider failed: %s", exc)
        raise MarketDataUnavailableError(" | ".join(failures) or "No provider returned data")


def _provider_from_name(name: str) -> MarketDataProvider | None:
    normalized = name.strip().lower()
    if not normalized:
        return None
    if normalized == "yfinance":
        return YFinanceMarketDataProvider()
    logger.warning("Configured market-data provider is not implemented: %s", normalized)
    return None


@lru_cache
def get_market_data_provider() -> MarketDataProvider:
    settings = get_settings()
    providers: list[MarketDataProvider] = []
    seen: set[str] = set()
    for name in (settings.market_data_primary, settings.market_data_fallback):
        provider = _provider_from_name(name)
        if provider is not None and provider.name not in seen:
            seen.add(provider.name)
            providers.append(provider)
    if not providers:
        raise MarketDataUnavailableError("No supported market-data provider is configured")
    return FallbackMarketDataProvider(tuple(providers))