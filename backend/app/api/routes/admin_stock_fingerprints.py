from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.dependencies import CurrentAdmin, DatabaseSession
from sahmi_kasban.fingerprint import (
    AISignatureCritic,
    FingerprintExtractor,
    StockAlgorithmicSignature,
    StockSignatureRegistry,
)
from sahmi_kasban.indicators import prepare_candles
import pandas as pd


router = APIRouter(prefix="/admin/stock-fingerprints", tags=["admin-stock-fingerprints"])


class RebuildSignatureRequest(BaseModel):
    ticker: str | None = None


class SignatureItemResponse(BaseModel):
    ticker: str
    updated_at: str
    overall_quality_score: float
    approved_by_critic: bool
    critic_confidence: float
    critic_summary: str
    dominant_cycle_sessions: int
    cycle_stability_score: float
    avg_sweep_depth_pct: float
    bounce_probability_pct: float


class SignatureListResponse(BaseModel):
    total_count: int
    signatures: list[SignatureItemResponse]


def _mock_candles(ticker: str) -> pd.DataFrame:
    base_price = 50.0 + (hash(ticker) % 30)
    data = []
    price = base_price
    for i in range(120):
        change = (i % 7 - 3) * 0.4
        price = max(5.0, price + change)
        high = price + 1.2
        low = max(0.5, price - 1.1)
        data.append(
            {
                "timestamp": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i),
                "open": price - 0.2,
                "high": high,
                "low": low,
                "close": price,
                "volume": 200_000 + (i % 5) * 50_000,
            }
        )
    return pd.DataFrame(data)


@router.get("/list", response_model=SignatureListResponse)
def list_signatures(
    current_admin: CurrentAdmin,
) -> SignatureListResponse:
    registry = StockSignatureRegistry()
    items: list[SignatureItemResponse] = []
    signatures = registry.list_signatures()

    for symbol, sig in sorted(signatures.items()):
        items.append(
            SignatureItemResponse(
                ticker=symbol,
                updated_at=sig.updated_at,
                overall_quality_score=sig.overall_quality_score,
                approved_by_critic=sig.ai_critic.approved,
                critic_confidence=sig.ai_critic.confidence,
                critic_summary=sig.ai_critic.summary,
                dominant_cycle_sessions=sig.time_cycle.dominant_cycle_sessions,
                cycle_stability_score=sig.time_cycle.stability_score,
                avg_sweep_depth_pct=sig.accumulation_sweep.avg_sweep_depth_pct,
                bounce_probability_pct=sig.accumulation_sweep.bounce_probability_pct,
            )
        )

    return SignatureListResponse(total_count=len(items), signatures=items)


@router.post("/rebuild", response_model=SignatureListResponse)
async def rebuild_signatures(
    payload: RebuildSignatureRequest,
    current_admin: CurrentAdmin,
) -> SignatureListResponse:
    registry = StockSignatureRegistry()
    critic = AISignatureCritic()
    extractor = FingerprintExtractor()

    tickers = [payload.ticker.upper()] if payload.ticker else ["COMI", "EAST", "EKHO", "HRHO", "SWDY"]
    from datetime import datetime, timezone

    for symbol in tickers:
        candles = prepare_candles(_mock_candles(symbol))
        tc = extractor.extract_time_cycle(candles)
        acc = extractor.extract_accumulation_sweep(candles)

        ai_eval = await critic.evaluate_signature(symbol, tc, acc)

        quality_score = max(
            0.0,
            min(
                100.0,
                (tc.stability_score * 0.4)
                + (acc.bounce_probability_pct * 0.4)
                + (ai_eval.confidence * 0.2),
            ),
        )

        sig = StockAlgorithmicSignature(
            ticker=symbol,
            updated_at=datetime.now(timezone.utc).isoformat(),
            time_cycle=tc,
            accumulation_sweep=acc,
            ai_critic=ai_eval,
            overall_quality_score=round(quality_score, 2),
        )
        registry.save_signature(sig)

    return list_signatures(current_admin)


@router.get("/export-excel")
def export_excel(
    current_admin: CurrentAdmin,
) -> FileResponse:
    registry = StockSignatureRegistry()
    temp_dir = Path(tempfile.gettempdir())
    out_file = temp_dir / "stock_fingerprints.xlsx"
    exported_path = registry.export_to_excel(out_file)

    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if exported_path.suffix == ".xlsx"
        else "text/csv"
    )

    return FileResponse(
        path=exported_path,
        filename=exported_path.name,
        media_type=media_type,
    )
