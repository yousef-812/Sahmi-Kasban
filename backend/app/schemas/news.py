from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NewsArticleResponse(BaseModel):
    id: UUID
    title: str
    summary: str
    url: str
    source_name: str
    source_key: str
    image_url: str | None
    published_at: datetime
    sentiment: str | None
    tickers: list[str]

    model_config = {"from_attributes": True}


class NewsListResponse(BaseModel):
    items: list[NewsArticleResponse]
    total: int
    has_more: bool
