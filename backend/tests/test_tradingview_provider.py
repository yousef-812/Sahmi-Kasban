import json

from reusable_data_fetcher import TradingViewConnector

from app.core.config import Settings
from app.market_data.tradingview import (
    _history_count,
    _normalize_candles,
    _tradingview_interval,
)


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
