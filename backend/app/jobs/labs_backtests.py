from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.market_calendar import EGXTradingCalendar
from app.market_data.provider import get_market_data_provider
from app.models import LabsBacktestJob
from app.services.labs_backtest_jobs import (
    claim_next_labs_job,
    recover_stale_labs_jobs,
)
from app.services.labs_daily_backtests import (
    LabsDailyBacktestResult,
    execute_daily_report_backtest,
)

logger = logging.getLogger(__name__)

_STALE_RECOVERY_MINUTES = 15
_STALE_RECOVERY_EVERY_CYCLES = 30


def _tracked_point_payload(point: Any) -> dict[str, object]:
    return {
        "time": point.timestamp.strftime("%H:%M"),
        "price": round(float(point.price), 4),
        "high": round(float(point.high), 4),
        "low": round(float(point.low), 4),
    }


def _session_payload(trade: Any) -> dict[str, object]:
    return {
        "target_session_date": trade.target_session_date.isoformat(),
        "report_id": str(trade.report_id),
        "rank": trade.rank,
        "ticker": trade.ticker,
        "score": trade.score,
        "price_at_analysis": (
            round(float(trade.price_at_analysis), 4)
            if trade.price_at_analysis is not None
            else None
        ),
        "targets": [round(float(target), 4) for target in trade.targets],
        "stop_loss": (
            round(float(trade.stop_loss), 4)
            if trade.stop_loss is not None
            else None
        ),
        "session_open": (
            round(float(trade.session_open), 4)
            if trade.session_open is not None
            else None
        ),
        "exit_price": (
            round(float(trade.exit_price), 4)
            if trade.exit_price is not None
            else None
        ),
        "exit_reason": trade.exit_reason,
        "hit": trade.hit,
        "minutes_to_exit": trade.minutes_to_exit,
        "return_pct": trade.return_pct,
        "tracked": [
            _tracked_point_payload(point) for point in trade.tracked
        ],
    }


def _result_json(result: LabsDailyBacktestResult) -> dict[str, Any]:
    return {
        "params": dict(result.params),
        "summary": dict(result.summary),
        "sessions": [_session_payload(trade) for trade in result.sessions],
    }


async def _run_job(db: Session, job: LabsBacktestJob) -> None:
    provider = get_market_data_provider()
    try:
        result = await execute_daily_report_backtest(
            db,
            provider,
            start_date=job.start_date,
            end_date=job.end_date,
            rank=job.rank,
            exit_mode=job.exit_mode,
            calendar=EGXTradingCalendar.from_settings(),
        )
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        db.rollback()
        current = db.get(LabsBacktestJob, job.id)
        if current is not None:
            current.status = "failed"
            current.error_message = str(exc)[:1000]
            current.completed_at = datetime.now(UTC)
            db.commit()
        logger.warning("Labs backtest job %s failed: %s", job.id, exc)
        return

    current = db.get(LabsBacktestJob, job.id)
    if current is None:
        return
    current.status = "complete"
    current.result_json = _result_json(result)
    current.error_message = None
    current.completed_at = datetime.now(UTC)
    db.commit()
    logger.info(
        "Labs backtest job %s complete: %s trades / %s hits",
        job.id,
        result.summary.get("trades"),
        result.summary.get("hits"),
    )


async def process_next_labs_backtest() -> bool:
    with SessionLocal() as db:
        job = claim_next_labs_job(db)
        if job is None:
            return False
        await _run_job(db, job)
    return True


async def run_labs_backtest_scheduler() -> None:
    """Run queued labs backtests on the isolated replay worker (test machine)."""

    settings = get_settings()
    logger.info("Labs backtest worker started on the isolated process group")
    cycles = 0
    while True:
        try:
            if cycles % _STALE_RECOVERY_EVERY_CYCLES == 0:
                with SessionLocal() as db:
                    recovered = recover_stale_labs_jobs(
                        db,
                        stale_minutes=_STALE_RECOVERY_MINUTES,
                    )
                if recovered:
                    logger.info("Requeued %s stale labs backtest job(s)", recovered)
            worked = await process_next_labs_backtest()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Labs backtest worker cycle failed")
            worked = False
        cycles += 1
        await asyncio.sleep(
            settings.historical_replay_active_poll_seconds
            if worked
            else settings.historical_replay_idle_poll_seconds
        )
