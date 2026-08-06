"""Force an immediate TradingView catalog refresh and report Arabic coverage.

Run inside the deployed container:

    python -m app.jobs.force_refresh_catalog

Useful after shipping a scanner/localization change so Arabic names land in the
database right away instead of waiting for the next 12h staleness window.
"""

import asyncio
import logging

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.market_data.catalog import refresh_market_instrument_catalog
from app.market_data.egx_symbols import has_arabic_text
from app.models import MarketInstrumentCatalog

logging.basicConfig(level=logging.INFO)


def main() -> None:
    async def _run() -> None:
        db = SessionLocal()
        try:
            refreshed = await refresh_market_instrument_catalog(db)
        finally:
            db.close()

        db = SessionLocal()
        try:
            total = db.scalar(
                select(func.count())
                .select_from(MarketInstrumentCatalog)
                .where(MarketInstrumentCatalog.active.is_(True))
            )
            rows = db.execute(
                select(MarketInstrumentCatalog)
                .where(MarketInstrumentCatalog.active.is_(True))
                .order_by(MarketInstrumentCatalog.ticker)
            ).scalars()
            arabic_rows = [
                (row.ticker, row.description)
                for row in rows
                if has_arabic_text(row.description)
            ]
        finally:
            db.close()

        print(f"refreshed={refreshed}")
        print(f"active_total={total}")
        print(f"arabic_descriptions={len(arabic_rows)}")
        for ticker, description in arabic_rows[:25]:
            print(f"  {ticker}: {description}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
