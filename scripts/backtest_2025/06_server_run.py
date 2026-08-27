from __future__ import annotations

import asyncio
import json
import multiprocessing as mp
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/backend")

from sahmi_kasban.indicators import enrich_indicators, prepare_candles  # noqa: E402
from sahmi_kasban.models import AnalysisConfig  # noqa: E402
from sahmi_kasban.orchestrator import SahmiKasbanAnalyzer  # noqa: E402

MIN_HISTORY = 200
MIN_TURNOVER_EGP = 1_000_000.0
MIN_NONZERO_VOL_RATIO = 0.80
SIGNAL_PRIORITY = {"BUY": 2, "WATCH": 1, "AVOID": 0}
FETCH_COUNT = 3000

OUT = Path("/tmp/bt_output")
CANDLE_DIR = OUT / "candles"
PREPARED_DIR = OUT / "prepared"
for directory in (CANDLE_DIR, PREPARED_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def load_universe() -> list[str]:
    universe_file = OUT / "universe.json"
    if universe_file.exists():
        return json.loads(universe_file.read_text(encoding="utf-8"))["symbols"]
    from app.market_data.egx_symbols import EGX_SEED_SYMBOLS

    return list(EGX_SEED_SYMBOLS)


async def fetch_candles() -> None:
    from reusable_data_fetcher import StockDataFetcher

    universe = load_universe()
    missing = [t for t in universe if not (CANDLE_DIR / f"{t}.csv").exists()]
    if not missing:
        print(f"[fetch] all candles present ({len(universe)})", flush=True)
        return
    fetcher = StockDataFetcher(pool_size=2)
    ok = 0
    try:
        for index, ticker in enumerate(missing, start=1):
            rows = await fetcher.get_historical_data(ticker, "EGX", "1D", FETCH_COUNT)
            if rows:
                pd.DataFrame(rows).to_csv(CANDLE_DIR / f"{ticker}.csv", index=False)
                ok += 1
            if index % 25 == 0:
                print(f"[fetch] {index}/{len(missing)} ok={ok}", flush=True)
            await asyncio.sleep(0.25)
    finally:
        await fetcher.close()
    print(f"[fetch] done ok={ok} failed={len(missing) - ok}", flush=True)


def prepare_one(ticker: str) -> None:
    out_path = PREPARED_DIR / f"{ticker}.pkl"
    if out_path.exists():
        return
    csv_path = CANDLE_DIR / f"{ticker}.csv"
    if not csv_path.exists():
        return
    frame = pd.read_csv(csv_path)
    if "timestamp" in frame.columns:
        frame["timestamp"] = pd.to_datetime(
            frame["timestamp"], unit="s", errors="coerce", utc=True
        )
    frame = (
        frame.dropna(subset=["timestamp"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    try:
        prepared = enrich_indicators(prepare_candles(frame))
    except Exception as exc:
        print(f"[prepare] {ticker} FAILED: {exc}", flush=True)
        return
    prepared.to_pickle(out_path)


def prepare_all() -> None:
    universe = load_universe()
    tickers = [t for t in universe if (CANDLE_DIR / f"{t}.csv").exists()]
    for index, ticker in enumerate(tickers, start=1):
        prepare_one(ticker)
        if index % 50 == 0:
            print(f"[prepare] {index}/{len(tickers)}", flush=True)
    print(f"[prepare] done {len(tickers)}", flush=True)


def build_calendar(year: int) -> list[str]:
    days: set[date] = set()
    for path in PREPARED_DIR.glob("*.pkl"):
        df = pd.read_pickle(path)
        days.update(pd.to_datetime(df["timestamp"], utc=True).dt.date)
    year_days = sorted(d for d in days if d.year == year)
    payload = {"count": len(year_days), "dates": [d.isoformat() for d in year_days]}
    (OUT / f"sessions_{year}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[calendar] {year} days: {len(year_days)}", flush=True)
    return [d.isoformat() for d in year_days]


def _load_all(tickers: list[str]) -> dict[str, tuple[pd.DataFrame, np.ndarray]]:
    frames: dict[str, tuple[pd.DataFrame, np.ndarray]] = {}
    for ticker in tickers:
        df = pd.read_pickle(PREPARED_DIR / f"{ticker}.pkl")
        if df.empty:
            continue
        df = df.sort_values("timestamp").reset_index(drop=True)
        dates = df["timestamp"].dt.date.to_numpy(dtype=object)
        frames[ticker] = (df, dates)
    return frames


def _pick_for_session(
    session_date: date,
    frames: dict[str, tuple[pd.DataFrame, np.ndarray]],
    analyzer: SahmiKasbanAnalyzer,
) -> dict:
    best: dict | None = None
    for ticker, (df, dates) in frames.items():
        cutoff = int(np.searchsorted(dates, session_date, side="left"))
        if cutoff < MIN_HISTORY:
            continue
        history = df.iloc[:cutoff]
        recent = history.tail(20)
        close = recent["close"].to_numpy(dtype=float)
        volume = recent["volume"].to_numpy(dtype=float)
        volume = np.nan_to_num(volume)
        turnover = float((close * volume).mean())
        nonzero_ratio = float((volume > 0).mean())
        if turnover < MIN_TURNOVER_EGP or nonzero_ratio < MIN_NONZERO_VOL_RATIO:
            continue
        try:
            report = analyzer.analyze_prepared(ticker, history)
        except Exception:
            continue
        signal = str(report.signal).upper()
        if signal not in {"BUY", "WATCH"}:
            continue
        key = (
            int(report.qualified),
            SIGNAL_PRIORITY.get(signal, 0),
            int(round(report.final_score * 100)),
            round(report.confidence, 6),
            round(turnover, 2),
        )
        candidate = {
            "key": key,
            "ticker": ticker,
            "score": round(report.final_score, 4),
            "signal": signal,
            "qualified": bool(report.qualified),
            "confidence": round(report.confidence, 4),
            "turnover_egp": round(turnover, 2),
            "cutoff": cutoff,
            "total_rows": len(df),
        }
        if best is None or key > best["key"]:
            best = candidate
    return {"date": session_date.isoformat(), "pick": best}


def _worker(args: tuple[list[str], list[str]]) -> list[dict]:
    tickers, session_strs = args
    frames = _load_all(tickers)
    analyzer = SahmiKasbanAnalyzer(
        AnalysisConfig(
            capital=150_000.0,
            risk_per_trade=0.01,
            min_history=MIN_HISTORY,
        )
    )
    sessions = [date.fromisoformat(s) for s in session_strs]
    rows: list[dict] = []
    for index, session_date in enumerate(sessions, start=1):
        result = _pick_for_session(session_date, frames, analyzer)
        pick = result["pick"]
        if pick is not None:
            df, _dates = frames[pick["ticker"]]
            cutoff = pick["cutoff"]
            if cutoff < len(df):
                row = df.iloc[cutoff]
                entry = float(row["open"])
                exit_price = float(row["close"])
                pick["entry"] = round(entry, 4)
                pick["exit"] = round(exit_price, 4)
                pick["return_pct"] = round((exit_price / entry - 1.0) * 100.0, 4)
                pick["traded"] = True
            else:
                pick["entry"] = None
                pick["exit"] = None
                pick["return_pct"] = None
                pick["traded"] = False
        result.pop("pick")
        result.update(pick or {})
        rows.append(result)
        if index % 30 == 0:
            print(
                f"[sim] {index}/{len(sessions)} {session_date} -> "
                f"{pick and pick.get('ticker')}",
                flush=True,
            )
    return rows


def run_simulation(sessions: list[str], year: int) -> None:
    tickers = sorted(p.stem for p in PREPARED_DIR.glob("*.pkl"))
    print(f"[sim {year}] sessions={len(sessions)} tickers={len(tickers)}", flush=True)
    chunks = np.array_split(sessions, 2)
    chunks = [[d for d in chunk] for chunk in chunks]
    with mp.Pool(2) as pool:
        results = pool.map(_worker, [(tickers, chunk) for chunk in chunks])
    flat = [row for chunk in results for row in chunk]
    flat.sort(key=lambda r: r["date"])
    (OUT / f"trades_{year}.json").write_text(
        json.dumps(flat, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    traded = [r for r in flat if r.get("traded")]
    compounded = (np.prod([1 + r["return_pct"] / 100.0 for r in traded]) - 1) * 100
    wins = sum(1 for r in traded if r["return_pct"] > 0)
    summary = {
        "year": year,
        "total_sessions": len(flat),
        "traded": len(traded),
        "no_trade_days": len(flat) - len(traded),
        "compounded_return_pct": round(float(compounded), 2),
        "win_rate_pct": round(wins / len(traded) * 100, 2) if traded else 0.0,
        "starting_balance": 10000.0,
        "final_balance": round(10000.0 * (1 + compounded / 100.0), 2),
    }
    (OUT / f"summary_{year}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"[sim {year}] DONE {summary}", flush=True)


def main() -> None:
    years = [int(arg) for arg in sys.argv[1:]] or [2025]
    asyncio.run(fetch_candles())
    prepare_all()
    for year in years:
        sessions = build_calendar(year)
        run_simulation(sessions, year)


if __name__ == "__main__":
    main()
