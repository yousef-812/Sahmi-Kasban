from __future__ import annotations

EGX30_INDEX_NAME = "EGX30"
EGX70_INDEX_NAME = "EGX70"

# Curated EGX30 proxy seeded from the 2025 correlation study: tickers whose
# returns tracked the EGX30 distinctly better than the EGX70 among the most
# liquid names. Meant as a deterministic default; the authoritative list can be
# supplied at call time via egx30_tickers.
EGX30_TICKERS: frozenset[str] = frozenset(
    {
        "ABUK",
        "ADIB",
        "CCAP",
        "COMI",
        "EAST",
        "EFIH",
        "EGAL",
        "ETEL",
        "FWRY",
        "HRHO",
        "ISPH",
        "ORAS",
        "TMGH",
    }
)


def resolve_index_for_ticker(
    ticker: str | None,
    *,
    egx30_tickers: frozenset[str] | set[str] | None = None,
) -> str:
    symbol = (ticker or "").strip().upper()
    members = frozenset(egx30_tickers or EGX30_TICKERS)
    return EGX30_INDEX_NAME if symbol in members else EGX70_INDEX_NAME
