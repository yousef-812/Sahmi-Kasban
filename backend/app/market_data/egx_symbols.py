from __future__ import annotations

import re

from app.market_data.types import MarketInstrument, UnknownTickerError

# Seed registry migrated from the legacy EGX-Pilot universe and deduplicated.
# It is now only a startup/failure fallback. The persistent catalog is refreshed
# from TradingView and is authoritative for user-facing search and analysis.
EGX_SEED_SYMBOLS: tuple[str, ...] = (
    "COMI",
    "CBKD",
    "HRHO",
    "EAST",
    "ESRS",
    "AUTO",
    "ETEL",
    "FWRY",
    "JUFO",
    "KZPC",
    "MFPC",
    "ORWE",
    "PHDC",
    "TMGH",
    "ADIB",
    "AKHO",
    "ALCN",
    "ALEX",
    "AMER",
    "ASEC",
    "ASEM",
    "ATQA",
    "ATRC",
    "BHGR",
    "BMCL",
    "BTFH",
    "BTRC",
    "BUFH",
    "CIRA",
    "CLHO",
    "CNIN",
    "DCRC",
    "DICA",
    "DIAL",
    "DORA",
    "DSCW",
    "DSGI",
    "DTPC",
    "EGCH",
    "EGCI",
    "EGLG",
    "EGTS",
    "EIIF",
    "ELEC",
    "ELSH",
    "EMFD",
    "EMIS",
    "EQS",
    "ESEG",
    "ESER",
    "ETAB",
    "EWAP",
    "FIPP",
    "GASC",
    "GCAP",
    "GSPC",
    "GURO",
    "GYPC",
    "HELI",
    "ICAP",
    "IDBT",
    "IDRE",
    "IETF",
    "INCO",
    "INTE",
    "ISMA",
    "ISPH",
    "KIMA",
    "LCHE",
    "LEAD",
    "MABA",
    "MADR",
    "MAEX",
    "MARA",
    "MASR",
    "MBCO",
    "MCDR",
    "MICH",
    "MIKR",
    "MILA",
    "MOIL",
    "MRHL",
    "MTIE",
    "NAHO",
    "NCEM",
    "NCCI",
    "NCFE",
    "NISC",
    "NORD",
    "OLFI",
    "OMAO",
    "ORHD",
    "ORKA",
    "ORPI",
    "OTMT",
    "PHAR",
    "PIOH",
    "PLCC",
    "PMAS",
    "PNBH",
    "POUL",
    "PRCL",
    "PTRA",
    "PWTG",
    "RAYA",
    "ROSE",
    "RPAS",
    "SACE",
    "SALM",
    "SAMT",
    "SARA",
    "SAUD",
    "SCEM",
    "SCFC",
    "SEET",
    "SFEG",
    "SHFT",
    "SHIP",
    "SIDM",
    "SIIC",
    "SKJP",
    "SKPC",
    "SMFR",
    "SMIT",
    "SODI",
    "SOLV",
    "SPIN",
    "SPMD",
    "SSDC",
    "STIV",
    "STPK",
    "SUGR",
    "SVCE",
    "SWDY",
    "SYST",
    "TACT",
    "TAQA",
    "TASE",
    "TEGT",
    "TMOS",
    "TOPA",
    "TPHC",
    "TRCO",
    "TRST",
    "UEGC",
    "UFGC",
    "UNIP",
    "UPCA",
    "VACS",
    "WATI",
    "WEGY",
    "WINO",
    "WTCA",
    "ZAIM",
    "EKHO",
    "KORA",
)

EGX_SYMBOL_SET = frozenset(EGX_SEED_SYMBOLS)
_TICKER_PATTERN = re.compile(r"^[A-Z0-9]{1,24}$")

# Curated Arabic company names for the most-traded EGX blue chips. These are
# used as a deterministic fallback so Arabic-name search works even when the
# external scanner does not localize descriptions.
EGX_ARABIC_NAMES: dict[str, str] = {
    "COMI": "البنك التجاري الدولي",
    "CCAP": "القلعة القابضة",
    "TMGH": "طلعت مصطفى القابضة",
    "EAST": "الشرقية للدخان",
    "ORWE": "النساجون الشرقيون",
    "JUFO": "جهينة للصناعات الغذائية",
    "ETEL": "المصرية للاتصالات",
    "ALCN": "العربية للصناعات الدوائية",
    "BTFH": "بنك التعمير والإسكان",
    "PHDC": "بالم هيلز للتعمير",
    "HELI": "هيليوبوليس للإسكان والتعمير",
    "SIDM": "سيدي كرير للبتروكيماويات",
    "KIMA": "كيما",
    "ADIB": "بنك أبوظبي الإسلامي مصر",
    "WEGY": "وادي كوم أمبو لاستصلاح الأراضي",
    "RAYA": "راية القابضة للاستثمارات المالية",
    "KORA": "كوررا لتنمية الاستثمار (Korra)",
}


def has_arabic_text(value: str) -> bool:
    return any("\u0600" <= character <= "\u06ff" for character in value)


def sanitize_arabic_description(
    description: str,
    ticker: str,
    *,
    use_curated_fallback: bool = True,
) -> str:
    normalized_ticker = ticker.strip().upper()
    if use_curated_fallback:
        curated = EGX_ARABIC_NAMES.get(normalized_ticker)
        if curated:
            return curated
    if not description or not description.strip():
        curated = EGX_ARABIC_NAMES.get(normalized_ticker)
        return curated if curated else normalized_ticker
    if "?" in description or "\ufffd" in description:
        cleaned = re.sub(r"[\?\ufffd]+", " ", description).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned and (has_arabic_text(cleaned) or len(cleaned) >= 3):
            return cleaned
        curated = EGX_ARABIC_NAMES.get(normalized_ticker)
        return curated if curated else normalized_ticker
    return description.strip()


def normalize_egx_ticker(ticker: str) -> str:
    normalized = ticker.strip().upper().removesuffix(".CA")
    normalized = normalized.removeprefix("EGX:")
    if not _TICKER_PATTERN.fullmatch(normalized):
        raise UnknownTickerError(f"Invalid EGX ticker: {normalized or ticker}")
    return normalized


def to_yahoo_symbol(ticker: str) -> str:
    return f"{normalize_egx_ticker(ticker)}.CA"


def list_instruments(query: str = "", limit: int = 50) -> list[MarketInstrument]:
    normalized_query = query.strip().upper()
    matches = (ticker for ticker in EGX_SEED_SYMBOLS if not normalized_query or normalized_query in ticker)
    return [
        MarketInstrument(ticker=ticker, provider_symbol=f"EGX:{ticker}") for ticker in list(matches)[:limit]
    ]
