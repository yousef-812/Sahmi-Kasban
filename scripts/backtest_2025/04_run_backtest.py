from __future__ import annotations

import json
import multiprocessing as mp
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from sahmi_kasban.models import AnalysisConfig
from sahmi_kasban.orchestrator import SahmiKasbanAnalyzer

ROOT = Path(__file__).resolve().parents[2]
PREPARED_DIR = ROOT / "backtest_2025" / "data" / "prepared"

MIN_HISTORY = 200
MIN_TURNOVER_EGP = 1_000_000.0
MIN_NONZERO_VOL_RATIO = 0.80
SIGNAL_PRIORITY = {"BUY": 2, "WATCH": 1, "AVOID": 0}


def _load_all(tickers: list[str]) -> dict[str, tuple[pd.DataFrame, np.ndarray]]:
    frames: dict[str, tuple[pd.DataFrame, np.ndarray]] = {}
    for ticker in tickers:
        df = pd.read_parquet(PREPARED_DIR / f"{ticker}.parquet")
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
        started = time.perf_counter()
        result = _pick_for_session(session_date, frames, analyzer)
        pick = result["pick"]
        if pick is not None:
            df, dates = frames[pick["ticker"]]
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
        if index % 20 == 0:
            elapsed = time.perf_counter() - started
            remaining = elapsed * (len(sessions) - index)
            print(
                f"[{index}/{len(sessions)}] {session_date} -> {pick and pick.get('ticker')} "
                f"({elapsed:.1f}s/session, ~{remaining/60:.0f}min left)",
                flush=True,
            )
    return rows


def main() -> None:
    sessions = json.loads(
        (ROOT / "backtest_2025" / "sessions_2025.json").read_text(encoding="utf-8")
    )["dates"]
    tickers = sorted(
        p.stem for p in PREPARED_DIR.glob("*.parquet")
    )
    print(f"Sessions: {len(sessions)}, tickers: {len(tickers)}")
    chunks = np.array_split(sessions, 4)
    chunks = [c.tolist() for c in chunks]
    with mp.Pool(4) as pool:
        results = pool.map(_worker, [(tickers, chunk) for chunk in chunks])
    flat = [row for chunk in results for row in chunk]
    flat.sort(key=lambda r: r["date"])
    out_path = ROOT / "backtest_2025" / "trades_2025.json"
    out_path.write_text(
        json.dumps(flat, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    traded = [r for r in flat if r.get("traded")]
    no_trade = [r for r in flat if not r.get("traded")]
    total_return = (np.prod([1 + r["return_pct"] / 100.0 for r in traded]) - 1) * 100
    print(f"Trades: {len(traded)}, no-trade days: {len(no_trade)}")
    print(f"Compounded return (10k): {total_return:.2f}%")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
