import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import pytest
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistAddIn, WatchlistItemOut, WatchlistResponse


def test_watchlist_schemas() -> None:
    add_schema = WatchlistAddIn(ticker="comi")
    assert add_schema.ticker == "comi"

    item_out = WatchlistItemOut(
        ticker="COMI",
        added_at="2026-08-27T09:00:00Z",
        last_signal="BUY",
        last_score=85.5,
        last_price=75.25,
        last_change_pct=2.1,
    )
    assert item_out.ticker == "COMI"
    assert item_out.last_signal == "BUY"
    assert item_out.last_score == 85.5

    response = WatchlistResponse(
        items=[item_out],
        count=1,
        max_items=50,
    )
    assert response.count == 1
    assert response.max_items == 50
