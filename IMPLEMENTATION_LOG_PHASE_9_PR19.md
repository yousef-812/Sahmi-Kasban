# Phase 9 / PR #19 — Performance Experience

> Branch: `agent/phase-9-performance-experience`  
> Pull request: #19  
> Status: implementation complete; final validation in progress  
> Updated: 2026-07-26

This pull request builds transparent public performance statistics and the Flutter/admin experience on top of the server-authoritative ledger merged in PR #18.

## Implemented Backend scope

- authenticated summaries for the latest 7 or 30 due EGX report sessions;
- explicit data completeness using the frozen report-item count;
- positive, negative, and flat results with negative outcomes retained;
- average and median return, direction accuracy, target rates, and stop-loss rate;
- best and worst observations and rank 1–10 performance;
- transparent session history and per-report outcome drill-down;
- delayed-report administration queue and specific-report retry;
- CSV export that includes completed, pending, failed, and negative rows;
- audited OHLC corrections with before/after revision snapshots;
- parent-evaluation refresh and administrator audit events after correction;
- Alembic revision `0010_perf_experience` with full downgrade support.

## Implemented Flutter scope

- dashboard entry for the performance record;
- 7-session/30-session selector;
- visible completeness and delayed-data counts;
- average, median, positive/negative counts, direction, targets, and stop loss;
- best/worst cards and rank 1–10 comparison;
- session history and per-report outcome details;
- visible correction count and revision history;
- administrator performance operations screen for backfill, retry, CSV, and corrections;
- routing guards that keep administrator operations protected.

## Transparency boundaries

- performance history does not require unlocking the original paid report;
- original analysis payloads are not exposed by the performance APIs;
- EGX30 benchmark status is explicitly `not_available` rather than estimated;
- past performance is labelled as non-guaranteeing;
- live Firebase Push remains deferred and is not part of PR #19.

## Validation completed so far

- Repository lint passed on workflow `30190875560`.
- Backend/Core/PostgreSQL tests passed on workflow `30190875560`.
- Full Alembic upgrade/downgrade/rebuild passed after shortening PostgreSQL constraint names.
- Flutter formatting passed; the one analyzer namespace conflict was corrected on head `332964bcb65f6a288534d5c11d7b0ec5d82b6da9`.

The final merge gate must still pass Flutter analyze/tests and Android debug APK on the final normal commit.
