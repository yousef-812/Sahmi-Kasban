from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class SectorMomentumEngine(AnalysisEngine):
    """يقيّم زخم القطاع لتجنب شراء أسهم ممتازة في قطاعات هابطة.
    
    يعتمد على قيمة `sector_momentum_5d_pct` الممررة عبر الـ context 
    (والتي يحسبها الـ Backend كمتوسط عائد آخر 5 أيام لأهم أسهم القطاع).
    """
    name = "sector_momentum"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        sector_momentum_5d_pct = safe_float(context.get("sector_momentum_5d_pct"), 0.0)
        
        score = 50.0
        reasons: list[str] = []
        
        if sector_momentum_5d_pct > 3.0:
            score += 10.0
            reasons.append("Sector momentum is strongly bullish")
        elif sector_momentum_5d_pct > 0.0:
            score += 5.0
            reasons.append("Sector momentum is mildly bullish")
        elif sector_momentum_5d_pct < -3.0:
            score -= 15.0
            reasons.append("Sector momentum is strongly bearish (High systemic risk)")
        elif sector_momentum_5d_pct < -1.0:
            score -= 8.0
            reasons.append("Sector momentum is mildly bearish")
        else:
            reasons.append("Sector momentum is neutral")

        score = self.clamp(score)
        context["sector_momentum_score"] = score
        
        return EngineResult(
            name=self.name,
            score=score,
            confidence=85.0,
            details={
                "model_version": "sector-momentum-v1.0",
                "sector_momentum_5d_pct": round(sector_momentum_5d_pct, 2),
            },
            reasons=reasons,
        )
