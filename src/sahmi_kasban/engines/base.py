from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from sahmi_kasban.models import AnalysisConfig, EngineResult


class AnalysisEngine(ABC):
    name = "base"

    def __init__(self, config: AnalysisConfig):
        self.config = config

    @abstractmethod
    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        raise NotImplementedError

    @staticmethod
    def clamp(value: float) -> float:
        return max(0.0, min(100.0, value))
