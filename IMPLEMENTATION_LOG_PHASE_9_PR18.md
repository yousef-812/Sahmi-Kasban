# Phase 9 / PR #18 — Performance Ledger

> Branch: `agent/phase-9-performance-ledger`  
> Status: in progress  
> Started: 2026-07-26

This pull request builds the server-authoritative ledger used to measure every item in the daily Top 10 reports against the actual target EGX session.

Planned scope:

- immutable report-item outcomes, including negative outcomes;
- one idempotent evaluation state per report;
- deterministic OHLC, return, target, stop-loss, and direction calculations;
- incomplete-data retry without publishing partial success as complete;
- due-report backfill and administrator trigger/status APIs;
- PostgreSQL, Alembic, service, and API tests.
