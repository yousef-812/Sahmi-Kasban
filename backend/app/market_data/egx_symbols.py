from __future__ import annotations

from app.market_data.types import MarketInstrument, UnknownTickerError

# Seed registry migrated from the legacy EGX-Pilot universe and deduplicated.
# Production must replace or reconcile it with an authoritative licensed exchange feed.
EGX_SEED_SYMBOLS: tuple[str, ...] = (
    "COMI", "CBKD", "HRHO", "EAST", "ESRS", "AUTO", "ETEL", "FWRY",
    "JUFO", "KZPC", "MFPC", "ORWE", "PHDC", "TMGH", "ADIB", "AKHO",
    "ALCN", "ALEX", "AMER", "ASEC", "ASEM", "ATQA", "ATRC", "BHGR",
    "BMCL", "BTFH", "BTRC", "BUFH", "CIRA", "CLHO", "CNIN", "DCRC",
    "DICA", "DIAL", "DORA", "DSGI", "DTPC", "EGCH", "EGCI", "EGLG",
    "EGTS", "EIIF", "ELEC", "ELSH", "EMFD", "EMIS", "EQS", "ESEG",
    "ESER", "ETAB", "EWAP", "FIPP", "GASC", "GCAP", "GSPC", "GURO",
    "GYPC", "HELI", "ICAP", "IDBT", "IDRE", "IETF", "INCO", "INTE",
    "ISMA", "ISPH", "KIMA", "LCHE", "LEAD", "MABA", "MADR", "MAEX",
    "MARA", "MASR", "MBCO", "MCDR", "MICH", "MIKR", "MILA", "MOIL",
    "MRHL", "MTIE", "NAHO", "NCEM", "NCCI", "NCFE", "NISC", "NORD",
    "OLFI", "OMAO", "ORHD", "ORKA", "ORPI", "OTMT", "PHAR", "PIOH",
    "PLCC", "PMAS", "PNBH", "POUL", "PRCL", "PTRA", "PWTG", "RAYA",
    "ROSE", "RPAS", "SACE", "SALM", "SAMT", "SARA", "SAUD", "SCEM",
    "SCFC", "SEET", "SFEG", "SHFT", "SHIP", "SIDM", "SIIC", "SKJP",
    "SKPC", "SMFR", "SMIT", "SODI", "SOLV", "SPIN", "SPMD", "SSDC",
    "STIV", "STPK", "SUGR", "SVCE", "SWDY", "SYST", "TACT", "TAQA",
    "TASE", "TEGT", "TMOS", "TOPA", "TPHC", "TRCO", "TRST", "UEGC",
    "UFGC", "UNIP", "UPCA", "VACS", "WATI", "WEGY", "WINO", "WTCA",
    "ZAIM", "EKHO",
)

EGX_SYMBOL_SET = frozenset(EGX_SEED_SYMBOLS)


def normalize_egx_ticker(ticker: str) -> str:
    normalized = ticker.strip().upper().removesuffix(".CA")
    if normalized not in EGX_SYMBOL_SET:
        raise UnknownTickerError(f"Unsupported EGX ticker: {normalized or ticker}")
    return normalized


def to_yahoo_symbol(ticker: str) -> str:
    return f"{normalize_egx_ticker(ticker)}.CA"


def list_instruments(query: str = "", limit: int = 50) -> list[MarketInstrument]:
    normalized_query = query.strip().upper()
    matches = (
        ticker
        for ticker in EGX_SEED_SYMBOLS
        if not normalized_query or normalized_query in ticker
    )
    return [
        MarketInstrument(ticker=ticker, provider_symbol=f"{ticker}.CA")
        for ticker in list(matches)[:limit]
    ]