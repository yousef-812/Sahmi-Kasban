import asyncio
import json

import pytest

from app.core.config import Settings
from app.market_data import tradingview as tv_module
from app.market_data.tradingview import (
    TradingViewMarketDataProvider,
    _history_count,
    _normalize_candles,
    _tradingview_interval,
)
from reusable_data_fetcher import TradingViewConnector


def test_connection_defaults_match_legacy_egx_pilot() -> None:
    settings = Settings(_env_file=None)
    assert settings.market_data_primary == "tradingview"
    assert settings.market_data_fallback == "yfinance"
    assert settings.tradingview_websocket_url == TradingViewConnector.URL
    assert settings.tradingview_origin == TradingViewConnector.HEADERS["Origin"]
    assert settings.tradingview_auth_token == "unauthorized_user_token"


def test_provider_normalization_converts_timestamps_and_preserves_values() -> None:
    candles = _normalize_candles(
        [
            {
                "timestamp": 1_700_000_000,
                "open": 9,
                "high": 11,
                "low": 8,
                "close": 10,
                "volume": 900,
            },
            {
                "timestamp": 1_700_086_400,
                "open": 10.5,
                "high": 12.5,
                "low": 9.5,
                "close": 12,
                "volume": 1_200,
            },
        ]
    )
    assert len(candles) == 2
    assert candles[0]["timestamp"].endswith("+00:00")
    assert candles[0]["close"] == 10.0
    assert candles[1]["close"] == 12.0
    assert candles[1]["volume"] == 1200.0
    assert json.loads(json.dumps(candles)) == candles


def test_interval_and_history_count_mapping() -> None:
    assert _tradingview_interval("1d") == "1D"
    assert _tradingview_interval("4h") == "240"
    assert _history_count("1y", "1d") == 300
    assert _history_count("5y", "1d") == 1400


def test_provider_reuses_single_websocket_connector(monkeypatch: pytest.MonkeyPatch) -> None:
    """لا يُنشأ موصّل WebSocket جديد لكل سهم.

    فتح موصّل وإغلاقه لكل رمز يجعل التطبيق يُجري مئات مصافحات WebSocket مع
    data.tradingview.com أثناء تجديد السكانر، فيتجاوز TradingView حد الباقة
    المجانية بعد نحو 10 اتصالات ويرجع series_error: resolve error لكل الرموز
    المتبقية. تحقّقنا عملياً من IP فرانكفورت على 20 رمزاً: أول 10 نجحوا والباقي
    فشل. السكانر يعالج الرموز تباعاً، فاتصال واحد مشترك يكفي.
    """
    created: list[object] = []
    closed: list[object] = []

    class _FakeConnector:
        def __init__(self, *args: object, **kwargs: object) -> None:
            created.append(self)
            self.URL = ""
            self.HEADERS: dict[str, str] = {}
            self.auth_token = ""
            self.timeout_seconds = 0.0

        async def get_historical(
            self,
            symbol: str,
            *,
            timeframe: str,
            count: int,
            timeout: float,
        ) -> list[dict[str, float | int]]:
            return [
                {
                    "timestamp": 1_700_000_000,
                    "open": 9,
                    "high": 11,
                    "low": 8,
                    "close": 10,
                    "volume": 900,
                }
            ]

        async def close(self) -> None:
            closed.append(self)

    monkeypatch.setattr(tv_module, "TradingViewConnector", _FakeConnector)
    monkeypatch.setattr(tv_module, "_SHARED_CONNECTOR", None)

    provider = TradingViewMarketDataProvider()
    asyncio.run(provider.get_history("COMI", period="1mo", interval="1d"))
    asyncio.run(provider.get_history("HRHO", period="1mo", interval="1d"))

    assert len(created) == 1, "يجب إنشاء موصّل WebSocket واحداً مشتركاً لكل الرموز"
    assert closed == [], "لا يُغلق الموصّل بين الرموز"

    asyncio.run(tv_module.close_shared_connector())
    assert len(closed) == 1, "يُغلق الموصّل المشترك عند إيقاف التطبيق"


def test_close_shared_connector_swallows_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """فشل إغلاق الموصّل لا يجب أن يُفشل إيقاف التطبيق.

    في اختبارات TestClient قد يكون event loop قد أُغلِق قبل وصول cleanup، فيرمي
    ws.close() بـ RuntimeError: Event loop is closed. مهمة الإغلاق أن تكون لطيفة.
    """

    class _BrokenConnector:
        async def close(self) -> None:
            raise RuntimeError("Event loop is closed")

    monkeypatch.setattr(tv_module, "_SHARED_CONNECTOR", _BrokenConnector())

    asyncio.run(tv_module.close_shared_connector())  # must not raise

    assert tv_module._SHARED_CONNECTOR is None
