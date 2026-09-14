#!/usr/bin/env python3
"""CLI script to build and update stock algorithmic signatures using statistical extraction and AI Critic evaluation."""

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sahmi_kasban.fingerprint.critic import AISignatureCritic
from sahmi_kasban.fingerprint.extractor import FingerprintExtractor
from sahmi_kasban.fingerprint.models import StockAlgorithmicSignature
from sahmi_kasban.fingerprint.registry import StockSignatureRegistry
from sahmi_kasban.indicators import prepare_candles


def generate_mock_candles(ticker: str, count: int = 150) -> pd.DataFrame:
    """Generate deterministic synthetic candles for testing when live data is absent."""
    base_price = 50.0 + (hash(ticker) % 30)
    data = []
    price = base_price
    for i in range(count):
        change = (i % 7 - 3) * 0.4
        price = max(5.0, price + change)
        high = price + 1.2
        low = max(0.5, price - 1.1)
        data.append(
            {
                "timestamp": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i),
                "open": price - 0.2,
                "high": high,
                "low": low,
                "close": price,
                "volume": 200_000 + (i % 5) * 50_000,
            }
        )
    return pd.DataFrame(data)


async def build_signature_for_ticker(
    ticker: str,
    candles: pd.DataFrame,
    registry: StockSignatureRegistry,
    critic: AISignatureCritic,
) -> StockAlgorithmicSignature:
    prepared = prepare_candles(candles)
    extractor = FingerprintExtractor()

    time_cycle = extractor.extract_time_cycle(prepared)
    accumulation_sweep = extractor.extract_accumulation_sweep(prepared)

    ai_critique = await critic.evaluate_signature(ticker, time_cycle, accumulation_sweep)

    quality_score = max(
        0.0,
        min(
            100.0,
            (time_cycle.stability_score * 0.4)
            + (accumulation_sweep.bounce_probability_pct * 0.4)
            + (ai_critique.confidence * 0.2),
        ),
    )

    sig = StockAlgorithmicSignature(
        ticker=ticker.upper(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        time_cycle=time_cycle,
        accumulation_sweep=accumulation_sweep,
        ai_critic=ai_critique,
        overall_quality_score=round(quality_score, 2),
    )

    registry.save_signature(sig)
    return sig


async def main():
    parser = argparse.ArgumentParser(description="Build stock algorithmic signatures")
    parser.add_argument("--ticker", type=str, help="Specific ticker symbol (e.g. COMI)")
    parser.add_argument(
        "--output-dir", type=str, default="data/fingerprints", help="Storage directory"
    )
    args = parser.parse_args()

    registry = StockSignatureRegistry(args.output_dir)
    critic = AISignatureCritic()

    tickers = [args.ticker.upper()] if args.ticker else ["COMI", "EAST", "EKHO", "HRHO", "SWDY"]

    print(f"Building signatures for {len(tickers)} ticker(s)...")

    for symbol in tickers:
        candles = generate_mock_candles(symbol)
        sig = await build_signature_for_ticker(symbol, candles, registry, critic)
        print(
            f"[{symbol}] Signature built. Score: {sig.overall_quality_score}, AI Critic Approved: {sig.ai_critic.approved}"
        )

    print("Done! Registry contains", len(registry.list_signatures()), "signatures.")


if __name__ == "__main__":
    asyncio.run(main())
