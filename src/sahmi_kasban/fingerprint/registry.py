from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from sahmi_kasban.fingerprint.models import StockAlgorithmicSignature

DEFAULT_REGISTRY_DIR = Path("data/fingerprints")


class StockSignatureRegistry:
    """Persistent storage manager for stock algorithmic signatures."""

    def __init__(self, storage_dir: Path | str | None = None) -> None:
        self.storage_dir = Path(storage_dir) if storage_dir else DEFAULT_REGISTRY_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, StockAlgorithmicSignature] = {}

    def _file_path(self, ticker: str) -> Path:
        return self.storage_dir / f"{ticker.strip().upper()}.json"

    def get_signature(self, ticker: str) -> StockAlgorithmicSignature | None:
        symbol = ticker.strip().upper()
        if symbol in self._cache:
            return self._cache[symbol]

        path = self._file_path(symbol)
        if not path.is_file():
            return None

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            signature = StockAlgorithmicSignature.from_dict(data)
            self._cache[symbol] = signature
            return signature
        except Exception:
            return None

    def save_signature(self, signature: StockAlgorithmicSignature) -> None:
        symbol = signature.ticker.strip().upper()
        self._cache[symbol] = signature
        path = self._file_path(symbol)
        with path.open("w", encoding="utf-8") as f:
            json.dump(signature.to_dict(), f, ensure_ascii=False, indent=2)

    def list_signatures(self) -> dict[str, StockAlgorithmicSignature]:
        signatures: dict[str, StockAlgorithmicSignature] = {}
        for path in self.storage_dir.glob("*.json"):
            symbol = path.stem.upper()
            sig = self.get_signature(symbol)
            if sig is not None:
                signatures[symbol] = sig
        return signatures

    def export_to_excel(self, output_path: Path | str) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        signatures = self.list_signatures()
        rows: list[dict[str, Any]] = []

        for symbol, sig in sorted(signatures.items()):
            tc = sig.time_cycle
            acc = sig.accumulation_sweep
            critic = sig.ai_critic
            rows.append(
                {
                    "Ticker": symbol,
                    "Updated At": sig.updated_at,
                    "Overall Quality Score": sig.overall_quality_score,
                    "Dominant Cycle (Sessions)": tc.dominant_cycle_sessions,
                    "Cycle Stability Score": tc.stability_score,
                    "Next Cycle Window (Sessions)": tc.next_window_in_sessions,
                    "Avg Sweep Depth (%)": acc.avg_sweep_depth_pct,
                    "Bounce Probability (%)": acc.bounce_probability_pct,
                    "Avg Velocity (Sessions)": acc.avg_velocity_sessions,
                    "FVG Fill Preference (%)": acc.fvg_fill_preference_pct,
                    "AI Critic Approved": critic.approved,
                    "AI Critic Confidence": critic.confidence,
                    "AI Critic Summary": critic.summary,
                    "AI Critic Warnings": " | ".join(critic.warnings),
                }
            )

        if not rows:
            df = pd.DataFrame(
                columns=[
                    "Ticker",
                    "Updated At",
                    "Overall Quality Score",
                    "Dominant Cycle (Sessions)",
                    "Cycle Stability Score",
                    "Next Cycle Window (Sessions)",
                    "Avg Sweep Depth (%)",
                    "Bounce Probability (%)",
                    "Avg Velocity (Sessions)",
                    "FVG Fill Preference (%)",
                    "AI Critic Approved",
                    "AI Critic Confidence",
                    "AI Critic Summary",
                    "AI Critic Warnings",
                ]
            )
        else:
            df = pd.DataFrame(rows)

        try:
            df.to_excel(out, index=False, engine="openpyxl")
        except Exception:
            # Fallback to csv if openpyxl is unavailable
            csv_out = out.with_suffix(".csv")
            df.to_csv(csv_out, index=False, encoding="utf-8-sig")
            return csv_out

        return out
