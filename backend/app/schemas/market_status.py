from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

MarketWeekday = Literal[
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


class MarketSessionWindow(BaseModel):
    opens_at: str
    closes_at: str


class MarketStatusResponse(BaseModel):
    is_open: bool
    session: MarketSessionWindow
    timezone: str
    date: str
    next_open: str | None = None
    next_close: str | None = None
    day: MarketWeekday
    is_trading_day: bool
