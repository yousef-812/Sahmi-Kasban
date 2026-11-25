from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SymbolSentimentResponse(BaseModel):
    """درجة معنويات الأخبار لسهم خلال نافذة زمنية محددة."""

    ticker: str
    score: float = Field(ge=-1.0, le=1.0, description="متوسط مرجّح لمعنويات الأخبار في [-1, 1]")
    sample_size: int = Field(ge=0, description="عدد الأخبار داخل النافذة")
    coverage: Literal["insufficient", "low", "normal"]
    as_of: datetime
    window_days: int = Field(ge=1)
