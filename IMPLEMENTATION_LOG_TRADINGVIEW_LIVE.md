# TradingView Live Verification

## 2026-07-25

**Branch:** `agent/tradingview-provider`  
**Pull Request:** #8  
**Tester:** repository owner on Windows

## Full-data command under test

```python
await StockDataFetcher().get_full_data("COMI", market="EGX")
```

## Full-data result

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

## Realtime quote result

A separate market-hours call to `get_realtime_price("COMI", market="EGX")` returned:

| Field | Value |
|---|---:|
| symbol | COMI |
| market | EGX |
| provider_symbol | EGX:COMI |
| price | 140.0 |
| change | 0.03 |
| change_percent | 0.02 |
| open | 139.97 |
| source | tradingview_realtime |

This closes the external TradingView realtime `qsd` verification gate.

## Interpretation

- TradingView historical WebSocket retrieval succeeded with 200 real EGX candles.
- TradingView realtime WebSocket quote retrieval succeeded.
- OHLCV normalization and technical-indicator calculation succeeded.
- Yahoo Finance fundamentals retrieval succeeded.
- The full-data run used the designed historical-close fallback because its concurrent realtime request did not return before timeout; the dedicated realtime test later proved the quote path itself works.

## Local quality-suite result before fixes

| Check | Result |
|---|---|
| Backend compileall | passed |
| Backend Ruff | 7 `I001` import-order findings |
| Backend Pytest | 26 passed, 12 failed |
| Core compileall | passed |
| Core Ruff | passed |
| Core Pytest | 7 passed |

All 12 backend failures had the same cause: `jwt.exceptions.InvalidKeyError: HMAC key must not be empty` when no local `.env` existed.

## Fixes applied after the quality-suite run

- Added a short development-only default JWT key in `Settings` so local Development/Test runs do not require a `.env` file.
- Kept the default shorter than 32 characters, so Staging/Production validation still rejects startup unless a real secret is provided.
- Restored `conftest.py` to a clean import-only header rather than mutating environment variables between import blocks.
- Corrected confirmed First Party import ordering in:
  - `backend/app/market_data/tradingview.py`
  - `backend/tests/test_tradingview_provider.py`

A fresh local `ruff check` and `pytest` run is required to identify any remaining import-only findings and confirm that all 38 backend tests now pass.

## Repository-local GitHub Action experiment

At the repository owner's request, CI storage and execution logic were moved into the repository itself:

- Added `.github/actions/repository-ci/action.yml`.
- Added `.github/actions/repository-ci/run.sh`.
- Replaced five separate jobs with one `repository-ci` job.
- Removed `astral-sh/ruff-action`.
- Removed `actions/setup-python` and its external pip cache integration.
- Stored pip downloads under `.github/.cache/pip` during the job.
- Stored check logs under `.github/.ci-results` during the job.
- Added both generated directories to `.gitignore`.

Workflow run `30158915914` still failed before `Checkout repository` or any other step was created. GitHub returned `steps: None` for the single `repository-ci` job. This proves the remaining GitHub Actions failure happens before repository code, the local action, cache, or logs can run. The likely remaining causes are GitHub Actions account/repository availability, hosted-runner allocation, billing/minute limits, or an account-level Actions restriction.

## Storage incident

The earlier connector error (`No shard mapper found ... tmp_high_replication_nanobase_backfill`) was a transient internal storage failure while replacing a long Markdown file. Repository reads and writes now work. The live result and CI experiments are stored in this separate log to avoid repeatedly replacing the larger migration log through that previously unstable path.
