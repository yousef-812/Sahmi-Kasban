# Daily Report Performance Ledger

PR #18 introduces the auditable source of truth for measuring each stock selected in a daily Top 10 report against the actual target EGX session.

## Immutable source report

The evaluator never changes the original `MarketReport` or `MarketReportItem`. It reads the frozen values that existed when the report was generated:

- `price_at_analysis`;
- `expected_direction`;
- first and second targets when present;
- stop loss when present;
- report rank and score.

A completed item outcome is not overwritten by ordinary retry or backfill execution. Missing market data may move from `pending_data` to `complete`, but a completed historical result remains stable. A future correction workflow must create an explicit audited revision rather than silently replacing a completed record.

## Session eligibility

A report can be evaluated only after its `target_session_date` closes. The current deterministic gate uses the configured EGX calendar, `Africa/Cairo`, configured holidays, and the same configured post-session scan time used by the daily report job.

Calling the single-report evaluator before that gate raises `ReportEvaluationNotDueError` and creates no ledger row.

## Required market data

The evaluator requires one normalized candle whose Cairo session date exactly matches the report target date and whose open, high, low, and close are positive numeric values.

Outcome states:

- `complete`: a valid target-session candle was found and all deterministic calculations were stored;
- `pending_data`: provider failure, a missing target candle, or incomplete/invalid OHLC data; this state is retryable;
- `failed`: the frozen report item itself cannot be evaluated, for example because `price_at_analysis` is invalid.

A report evaluation is `complete` only when every report item is complete. Retryable gaps produce `partial`, never a misleading successful run.

## Deterministic calculations

All percentages are stored as integer basis points, where 100 basis points equal 1%.

```text
return_bp       = round((session_close / price_at_analysis - 1) * 10000)
max_upside_bp   = round((session_high  / price_at_analysis - 1) * 10000)
max_drawdown_bp = round((session_low   / price_at_analysis - 1) * 10000)
```

Direction correctness:

- `up`: target close is above `price_at_analysis`;
- `down`: target close is below `price_at_analysis`;
- `neutral`: absolute close return is no more than 50 basis points.

For an upward report item, a target is hit when the session high reaches or exceeds the target and the stop is hit when the session low reaches or falls below the stop. The comparisons are reversed for a downward item.

A stock can therefore hit a target and a stop during the same session. Both facts are retained because the ledger records observed session behavior rather than rewriting it into a favorable narrative.

## Negative results

Negative returns, incorrect directions, and stop-loss touches are normal completed outcomes. They are never filtered out and are counted in later 7-session and 30-session statistics.

Each complete outcome stores `negative_results_retained=true` and the evaluator version in its evidence payload.

## Idempotency and retry

- one `MarketReportEvaluation` exists per report;
- one `MarketReportItemOutcome` exists per report item;
- a recent `running` evaluation has a two-hour ownership window;
- a completed evaluation returns idempotently without calling the market provider again;
- a partial evaluation retries only items that are not already complete;
- concurrent creation is protected by database uniqueness and transaction handling.

## Administrator controls

Protected endpoints:

```text
GET  /api/v1/admin/operations/performance/evaluations
POST /api/v1/admin/operations/performance/evaluate-due
```

The backfill endpoint processes due incomplete reports in target-session order and returns completed, partial, failed, and skipped counts. It does not expose a public performance ranking; user-facing 7-session and 30-session pages belong to PR #19.
