from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class TimeCyclePattern:
    dominant_cycle_sessions: int = 35
    stability_score: float = 65.0
    cycle_phase_sessions: int = 0
    next_window_in_sessions: int = 5

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimeCyclePattern:
        return cls(
            dominant_cycle_sessions=int(data.get("dominant_cycle_sessions", 35)),
            stability_score=float(data.get("stability_score", 65.0)),
            cycle_phase_sessions=int(data.get("cycle_phase_sessions", 0)),
            next_window_in_sessions=int(data.get("next_window_in_sessions", 5)),
        )


@dataclass(slots=True)
class AccumulationSweepPattern:
    avg_sweep_depth_pct: float = 1.2
    bounce_probability_pct: float = 75.0
    avg_velocity_sessions: int = 4
    fvg_fill_preference_pct: float = 50.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AccumulationSweepPattern:
        return cls(
            avg_sweep_depth_pct=float(data.get("avg_sweep_depth_pct", 1.2)),
            bounce_probability_pct=float(data.get("bounce_probability_pct", 75.0)),
            avg_velocity_sessions=int(data.get("avg_velocity_sessions", 4)),
            fvg_fill_preference_pct=float(data.get("fvg_fill_preference_pct", 50.0)),
        )


@dataclass(slots=True)
class AICriticEvaluation:
    approved: bool = True
    confidence: float = 70.0
    summary: str = "Signature verified"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AICriticEvaluation:
        return cls(
            approved=bool(data.get("approved", True)),
            confidence=float(data.get("confidence", 70.0)),
            summary=str(data.get("summary", "Signature verified")),
            warnings=list(data.get("warnings", [])),
        )


@dataclass(slots=True)
class StockAlgorithmicSignature:
    ticker: str
    updated_at: str
    time_cycle: TimeCyclePattern
    accumulation_sweep: AccumulationSweepPattern
    ai_critic: AICriticEvaluation
    overall_quality_score: float = 70.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker.upper(),
            "updated_at": self.updated_at,
            "time_cycle": self.time_cycle.to_dict(),
            "accumulation_sweep": self.accumulation_sweep.to_dict(),
            "ai_critic": self.ai_critic.to_dict(),
            "overall_quality_score": round(self.overall_quality_score, 2),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StockAlgorithmicSignature:
        return cls(
            ticker=str(data.get("ticker", "")).upper(),
            updated_at=str(data.get("updated_at", "")),
            time_cycle=TimeCyclePattern.from_dict(data.get("time_cycle", {})),
            accumulation_sweep=AccumulationSweepPattern.from_dict(
                data.get("accumulation_sweep", {})
            ),
            ai_critic=AICriticEvaluation.from_dict(data.get("ai_critic", {})),
            overall_quality_score=float(data.get("overall_quality_score", 70.0)),
        )
