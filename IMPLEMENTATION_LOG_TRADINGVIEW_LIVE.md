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
- Corrected First Party import ordering in the TradingView provider and tests.
- Used Ruff's own fix output to correct the remaining `ta.trend` import order in `backend/reusable_data_fetcher.py`.

## Repository-local GitHub Actions implementation

At the repository owner's request, CI execution and temporary storage were moved into the repository workspace:

- Added `.github/actions/repository-ci/action.yml`.
- Added `.github/actions/repository-ci/run.sh`.
- Removed `astral-sh/ruff-action`.
- Removed `actions/setup-python` pip-cache integration.
- Stored pip downloads under `.github/.cache/pip` during each job.
- Stored check logs under `.github/.ci-results` during each job.
- Added both generated directories to `.gitignore`.
- Split CI into `repository-lint` and `repository-tests` jobs.
- The workflow calls the repository-owned `run.sh` directly after checkout. A direct script call was retained because the same script passed while the composite wrapper path failed in the PR merge environment.

The private repository had exhausted its included GitHub Actions allowance and returned `steps: None` before runner allocation. After the repository was made public, standard hosted runners started normally.

## Final CI verification

Workflow run `30160274508` completed successfully on commit `5988d945e8110e1f58b0831614337fc859a1ce0b`:

- `repository-lint`: success.
- `repository-tests`: success.
- PostgreSQL 16 service initialization: success.
- Core compile and Ruff: success.
- Backend compile and Ruff: success.
- Core and backend test suites: success.
- Alembic upgrade, downgrade to base, and rebuild: success.
- Live TradingView `COMI` smoke test: success.

The repository-owned script is fail-fast, so the successful job confirms every listed command completed with exit code zero. This closes the TradingView migration and verification gate.

## Storage incident

The earlier connector error (`No shard mapper found ... tmp_high_replication_nanobase_backfill`) was a transient internal storage failure while replacing a long Markdown file. Repository reads and writes now work. The live result and CI experiments are stored in this separate log to avoid repeatedly replacing the larger migration log through that previously unstable path.
