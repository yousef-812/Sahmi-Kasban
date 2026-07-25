import json

from app.core.config import Settings
from app.market_data.tradingview import (
    TRADINGVIEW_ORIGIN,
    TRADINGVIEW_UNAUTHORIZED_TOKEN,
    TRADINGVIEW_WEBSOCKET_URL,
    _frame_message,
    _history_count,
    _normalize_points,
    _parse_messages,
    _tradingview_interval,
)


def test_connection_defaults_match_legacy_egx_pilot() -> None:
    settings = Settings(_env_file=None)
    assert settings.market_data_primary == "tradingview"
    assert settings.market_data_fallback == "yfinance"
    assert settings.tradingview_websocket_url == TRADINGVIEW_WEBSOCKET_URL
    assert settings.tradingview_origin == TRADINGVIEW_ORIGIN
    assert settings.tradingview_auth_token == TRADINGVIEW_UNAUTHORIZED_TOKEN


def test_tradingview_message_round_trip() -> None:
    framed = _frame_message("set_auth_token", ["unauthorized_user_token"])
    messages = _parse_messages(framed)
    assert messages == [
        {"m": "set_auth_token", "p": ["unauthorized_user_token"]}
    ]


def test_parser_handles_multiple_framed_messages() -> None:
    first = _frame_message("chart_create_session", ["cs_test", ""])
    second = _frame_message("series_completed", ["cs_test", "s1"])
    assert _parse_messages(first + second) == [
        {"m": "chart_create_session", "p": ["cs_test", ""]},
        {"m": "series_completed", "p": ["cs_test", "s1"]},
    ]


def test_normalize_points_sorts_deduplicates_and_filters_invalid_rows() -> None:
    points = [
        {"v": [1_700_086_400, 10, 12, 9, 11, 1_000]},
        {"v": [1_700_000_000, 9, 11, 8, 10, 900]},
        {"v": [1_700_086_400, 10.5, 12.5, 9.5, 12, 1_200]},
        {"v": [1_700_172_800, 10, 9, 8, 11, 500]},
    ]
    candles = _normalize_points(points)
    assert len(candles) == 2
    assert candles[0]["close"] == 10.0
    assert candles[1]["close"] == 12.0
    assert candles[1]["volume"] == 1200.0
    assert json.loads(json.dumps(candles)) == candles


def test_interval_and_history_count_mapping() -> None:
    assert _tradingview_interval("1d") == "1D"
    assert _tradingview_interval("4h") == "240"
    assert _history_count("1y", "1d") == 300
    assert _history_count("5y", "1d") == 1400
