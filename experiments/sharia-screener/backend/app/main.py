from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.indicators import analyze
from app.providers.base import CSVProvider, MarketDataError
from app.providers.tradingview import TradingViewWebSocketProvider
import os

app = FastAPI(title="Sharia Screener API", version="0.1.0",
              description="Daily technical screening for a verified Sharia universe.")
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
UNIVERSE_FILE = DATA_DIR / "sharia_universe.txt"


def universe() -> list[str]:
    if not UNIVERSE_FILE.exists():
        return []
    return [line.strip() for line in UNIVERSE_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]


def analyze_symbol(symbol: str) -> dict:
    try:
        provider_name = os.getenv("DATA_PROVIDER", "csv").strip().lower()
        if provider_name == "tradingview":
            candles = TradingViewWebSocketProvider().daily_candles(symbol)
        elif provider_name == "csv":
            candles = CSVProvider(str(DATA_DIR)).daily_candles(symbol)
        else:
            raise MarketDataError(f"Unsupported DATA_PROVIDER: {provider_name}")
        result = analyze(candles, symbol)
        latest = candles["timestamp"].max()
        result["data_freshness"] = str(latest)
        return result
    except (MarketDataError, ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "ok", "service": "sharia-screener", "mode": os.getenv("DATA_PROVIDER", "csv").strip().lower()}


@app.get("/api/v1/universe")
def get_universe():
    return {"count": len(universe()), "symbols": universe(),
            "note": "Only include symbols after checking current official Sharia eligibility."}


@app.get("/api/v1/analysis/{symbol}")
def single_analysis(symbol: str):
    return analyze_symbol(symbol.upper())


@app.post("/api/v1/scan")
def scan_all():
    symbols = universe()
    if not symbols:
        raise HTTPException(status_code=409, detail="Sharia universe is empty. Add verified symbols first.")
    results, errors = [], []
    for symbol in symbols:
        try:
            results.append(analyze_symbol(symbol))
        except HTTPException as exc:
            errors.append({"symbol": symbol, "error": exc.detail})
    results.sort(key=lambda item: item["score"], reverse=True)
    return {"count": len(results), "failed_count": len(errors),
            "ranked": results, "errors": errors,
            "note": "Ranking is technical only; eligibility must be independently verified."}
