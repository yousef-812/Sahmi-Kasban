from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_data.catalog import (
    _parse_scanner_rows,
    _reconcile_scanner_rows,
    market_instrument_exists,
    search_market_instruments,
)
from app.models import MarketInstrumentCatalog


def test_tradingview_scanner_rows_keep_only_egx_stocks() -> None:
    rows = _parse_scanner_rows(
        {
            "data": [
                {
                    "s": "EGX:COMI",
                    "d": ["COMI", "Commercial International Bank", "EGX", "stock"],
                },
                {
                    "s": "EGX:DSCW",
                    "d": ["DSCW", "Dice Sport and Casual Wear", "EGX", "stock"],
                },
                {
                    "s": "NASDAQ:AAPL",
                    "d": ["AAPL", "Apple Inc.", "NASDAQ", "stock"],
                },
                {"s": "EGX:BAD SYMBOL", "d": []},
            ]
        }
    )

    assert [row.ticker for row in rows] == ["COMI", "DSCW"]
    assert rows[0].provider_symbol == "EGX:COMI"
    assert rows[0].description == "Commercial International Bank"


def test_authoritative_scanner_reconciliation_deactivates_stale_seed_symbols(
    db_session: Session,
) -> None:
    now = datetime.now(UTC)
    stale = MarketInstrumentCatalog(
        ticker="OLDX",
        provider_symbol="EGX:OLDX",
        exchange="EGX",
        description="Old inactive symbol",
        source="legacy_seed",
        active=True,
        last_seen_at=now,
    )
    kept = MarketInstrumentCatalog(
        ticker="KEEP",
        provider_symbol="EGX:KEEP",
        exchange="EGX",
        description="Old description",
        source="legacy_seed",
        active=True,
        last_seen_at=now,
    )
    db_session.add_all([stale, kept])
    db_session.commit()

    count, deactivated = _reconcile_scanner_rows(
        db_session,
        [
            MarketInstrumentCatalog(
                ticker="KEEP",
                provider_symbol="EGX:KEEP",
                exchange="EGX",
                description="Current listed company",
                source="tradingview_scanner",
                active=True,
                last_seen_at=now,
            )
        ],
        authoritative=True,
    )
    db_session.commit()

    rows = {
        row.ticker: row
        for row in db_session.scalars(
            select(MarketInstrumentCatalog).where(
                MarketInstrumentCatalog.ticker.in_(("OLDX", "KEEP"))
            )
        ).all()
    }
    assert count == 1
    assert deactivated == 1
    assert rows["OLDX"].active is False
    assert rows["KEEP"].active is True
    assert rows["KEEP"].source == "tradingview_scanner"
    assert rows["KEEP"].description == "Current listed company"


def test_dynamic_catalog_entries_are_searchable_and_analyzable(
    db_session: Session,
) -> None:
    db_session.add(
        MarketInstrumentCatalog(
            ticker="AALR",
            provider_symbol="EGX:AALR",
            exchange="EGX",
            description="General Co. for Land Reclamation",
            source="tradingview_scanner",
            active=True,
            last_seen_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    source, total, results = asyncio.run(
        search_market_instruments(db_session, query="Land Reclamation", limit=20)
    )

    assert source == "legacy_seed_registry"
    assert total >= 155
    assert [result.ticker for result in results] == ["AALR"]
    assert results[0].description == "General Co. for Land Reclamation"
    assert asyncio.run(market_instrument_exists(db_session, "AALR")) is True
