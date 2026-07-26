# Phase 9 / PR #18 — Performance Ledger

> Branch: `agent/phase-9-performance-ledger`  
> Pull request: #18  
> Status: implementation complete; validation in progress  
> Updated: 2026-07-26

This pull request builds the server-authoritative ledger used to measure every item in the daily Top 10 reports against the actual target EGX session.

## Implemented scope

- `MarketReportEvaluation`: one idempotent evaluation state per complete daily report.
- `MarketReportItemOutcome`: one deterministic outcome per frozen report item.
- Exact target-session candle matching using the configured EGX calendar and Cairo timezone.
- Integer basis-point calculations for close return, maximum upside, and maximum drawdown.
- Direction, first target, second target, and stop-loss result flags.
- Negative outcomes retained as valid completed results.
- `pending_data` for retryable provider or OHLC gaps and `failed` for invalid frozen report data.
- Completed outcomes are skipped on retry and completed reports return without another provider call.
- Due-report backfill in target-session order with completed, partial, failed, and skipped counts.
- Protected administrator endpoints for backfill execution and evaluation-state listing.
- Alembic revision `0009_report_performance` with full downgrade support.
- Service tests for session eligibility, negative-result retention, idempotency, retry, and backfill.
- API test for administrator-only access and end-to-end evaluation execution.
- Formula and audit documentation in `docs/PERFORMANCE_LEDGER.md`.

## Boundaries

PR #18 does not add public performance statistics or Flutter performance pages. Aggregated 7-session/30-session APIs, charts, administrator drill-down, CSV export, and explicit correction revisions belong to PR #19.

## Validation

The final merge gate must pass repository lint, Backend/Core/PostgreSQL tests, the complete Alembic upgrade/downgrade/rebuild cycle, Flutter format/analyze/tests, and Android debug APK build.
