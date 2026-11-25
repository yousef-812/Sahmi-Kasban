from __future__ import annotations

import math

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class NewsSentimentEngine(AnalysisEngine):
    """يقيّم معنويات الأخبار الممرّرة عبر الـ context.

    يعتمد على ``news_sentiment`` (float في -1..1) و``news_sample_size`` (int)
    اللذين يحسبهما الـ Backend من أخبار السهم. عند غياب المفاتيح أو صغر
    العيّنة يُرجع 50 محايدًا بثقة منخفضة حتى لا يضغط المحرك على الاتجاه.
    """

    name = "news_sentiment"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        raw_sentiment = context.get("news_sentiment")
        sample_size = max(0, int(safe_float(context.get("news_sample_size"), 0.0)))
        sentiment_value = safe_float(raw_sentiment, float("nan"))
        sentiment_valid = math.isfinite(sentiment_value)
        sentiment = max(-1.0, min(1.0, sentiment_value)) if sentiment_valid else 0.0

        if not sentiment_valid or sample_size <= 0:
            coverage = "insufficient"
        elif sample_size < 10:
            coverage = "low"
        else:
            coverage = "normal"

        reasons: list[str] = []
        if coverage == "insufficient":
            score = 50.0
            confidence = 20.0
            if raw_sentiment is None:
                reasons.append("News sentiment context is missing; neutral 50")
            elif not sentiment_valid:
                reasons.append("Non-numeric news sentiment treated as neutral 50")
            else:
                reasons.append("News sample size is zero; neutral 50")
        else:
            score = self.clamp(50.0 + 50.0 * sentiment)
            confidence = 50.0 if coverage == "low" else 85.0
            if score >= 55.0:
                reasons.append(
                    f"News sentiment is bullish ({sentiment:+.2f} from {sample_size} items)"
                )
            elif score <= 45.0:
                reasons.append(
                    f"News sentiment is bearish ({sentiment:+.2f} from {sample_size} items)"
                )
            else:
                reasons.append(
                    f"News sentiment is neutral ({sentiment:+.2f} from {sample_size} items)"
                )

        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "model_version": "news-sentiment-v1.0",
                "sentiment": round(sentiment, 4),
                "sample_size": sample_size,
                "coverage": coverage,
            },
            reasons=reasons,
        )
