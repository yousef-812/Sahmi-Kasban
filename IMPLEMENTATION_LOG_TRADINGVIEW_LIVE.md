# TradingView Live Verification

## 2026-07-25

**Branch:** `agent/tradingview-provider`  
**Pull Request:** #8  
**Tester:** repository owner on Windows

## Command under test

```python
await StockDataFetcher().get_full_data("COMI", market="EGX")
```

## Result

| Field | Value |
|---|---:|
| status | ok |
| ticker | COMI |
| market | EGX |
| price | 140.0 |
| price_source | historical_fallback |
| candle_count | 200 |
| last_close | 140.0 |
| last_volume | 3,972,917 |
| RSI | 61.44 |
| MACD | 1.36 |
| company_name | Commercial International Bank Egypt (CIB) S.A.E. |
| market_cap | approximately EGP 267.9 billion |

## Interpretation

- TradingView historical WebSocket retrieval succeeded with 200 real EGX candles.
- OHLCV normalization and technical-indicator calculation succeeded.
- Yahoo Finance fundamentals retrieval succeeded.
- The realtime quote timed out and the designed historical-close fallback returned 140.0. This is acceptable outside market hours, but realtime `qsd` verification during an EGX session remains a separate test gate.
- No transition to the next implementation phase should occur until the normal lint/test suites pass and the realtime quote path is tested during market hours.

## Storage incident

The earlier connector error (`No shard mapper found ... tmp_high_replication_nanobase_backfill`) was a transient internal storage failure while replacing a long Markdown file. Repository reads and small writes now work. This result is stored in a separate short append-only log to avoid rewriting the large migration log through that unstable path.
