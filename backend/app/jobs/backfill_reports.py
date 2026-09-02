import asyncio
import logging
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.market_calendar import EGXTradingCalendar
from app.market_data.catalog import ensure_market_instrument_catalog
from app.market_data.egx_symbols import EGX_SEED_SYMBOLS
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.market_data.universe import apply_market_health_quarantine
from app.models import Discussion, MarketReport, MarketScanRun
from app.services.daily_reports import generate_daily_top10_report
from app.services.report_performance import evaluate_market_report
from app.services.report_selection import enrich_daily_report_selection

logger = logging.getLogger(__name__)


class TruncatingMarketDataProvider:
    # Memory cache to share downloaded full histories across dates
    _cache = {}

    def __init__(self, original_provider, target_source_date):
        self.original_provider = original_provider
        self.target_source_date = target_source_date
        self.name = original_provider.name

    async def get_history(self, ticker: str, *, period: str, interval: str) -> CandleSeries:
        cache_key = (ticker, period, interval)
        if cache_key in self._cache:
            series = self._cache[cache_key]
        else:
            series = await self.original_provider.get_history(ticker, period=period, interval=interval)
            self._cache[cache_key] = series

        truncated_candles = []
        for c in series.candles:
            candle_date = datetime.fromisoformat(str(c["timestamp"])).date()
            if candle_date <= self.target_source_date:
                truncated_candles.append(c)

        if not truncated_candles:
            raise MarketDataUnavailableError(f"No candles found before {self.target_source_date}")

        last_candle = truncated_candles[-1]
        data_as_of = datetime.fromisoformat(str(last_candle["timestamp"]))

        return CandleSeries(
            ticker=series.ticker,
            provider=series.provider,
            interval=series.interval,
            period=series.period,
            fetched_at=series.fetched_at,
            data_as_of=data_as_of,
            fingerprint=series.fingerprint,
            candles=tuple(truncated_candles),
        )


class MockAIService:
    async def explain_stock_analysis(self, **kwargs):
        from sahmi_kasban.ai import AIProviderError

        raise AIProviderError("Skipping AI explanation for historical backfill")


async def backfill_one_day(
    db: Session,
    day: date,
    calendar: EGXTradingCalendar,
    tickers: list[str],
    truncating_provider,
    original_provider,
):
    target_date = calendar.next_trading_session(day)

    # Check if report already exists
    existing = db.scalar(
        select(MarketReport).where(
            MarketReport.target_session_date == target_date,
            MarketReport.status == "complete",
        )
    )

    report_id = None
    if existing:
        print(f"Report for target date {target_date} already exists.")
        report_id = existing.id
    else:
        print(f"Generating report for target date {target_date} (source: {day})...")
        truncating_provider.target_source_date = day
        mock_ai = MockAIService()
        moment = datetime.combine(day, time(18, 0, 0), tzinfo=calendar.timezone)

        result = await generate_daily_top10_report(
            db,
            provider=truncating_provider,
            ai_service=mock_ai,
            moment=moment,
            tickers=tickers,
        )
        report_id = result.report.id
        enrich_daily_report_selection(db, report_id=report_id)
        print(f"Successfully generated and enriched report for target date {target_date}")

    # Now evaluate its performance since it's historical
    if report_id:
        try:
            # We use original_provider (which has future data) to run evaluation
            await evaluate_market_report(
                db,
                report_id=report_id,
                provider=original_provider,
                moment=datetime.now(UTC),
            )
            print(f"Successfully evaluated performance for target date {target_date}")
        except Exception as eval_exc:
            print(f"Evaluation skipped/failed for target date {target_date}: {eval_exc}")


async def run_backfill():
    db = SessionLocal()

    # 1. Delete all old discussions
    try:
        deleted_discussions = db.query(Discussion).delete()
        db.commit()
        print(f"Deleted {deleted_discussions} discussions successfully.")
    except Exception as e:
        db.rollback()
        print("Error deleting discussions:", e)

    # 2. Reset any stale running scans
    try:
        deleted_runs = (
            db.query(MarketScanRun).filter(MarketScanRun.status == "running").update({"status": "failed"})
        )
        db.commit()
        print(f"Reset {deleted_runs} stale running scan records.")
    except Exception as e:
        db.rollback()
        print("Failed to reset running scans:", e)

    # 3. Backfill reports for 50 days in the past
    calendar = EGXTradingCalendar.from_settings()
    current_date = datetime.now(calendar.timezone).date()

    # Resolve tickers
    await ensure_market_instrument_catalog(db)
    universe = apply_market_health_quarantine(db)
    tickers = universe.tickers or EGX_SEED_SYMBOLS

    trading_days = []
    d = current_date
    while len(trading_days) < 50:
        d -= timedelta(days=1)
        if calendar.is_trading_session(d):
            trading_days.append(d)

    trading_days.reverse()

    original_provider = get_market_data_provider()
    truncating_provider = TruncatingMarketDataProvider(original_provider, current_date)

    print(f"Starting backfill and evaluation of reports for {len(trading_days)} trading days...")
    for day in trading_days:
        try:
            await backfill_one_day(db, day, calendar, tickers, truncating_provider, original_provider)
        except Exception as exc:
            import traceback

            traceback.print_exc()
            print(f"Failed to backfill day {day}: {exc}")

    db.close()
    print("Backfill and evaluation process finished.")


def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_backfill())


if __name__ == "__main__":
    main()
