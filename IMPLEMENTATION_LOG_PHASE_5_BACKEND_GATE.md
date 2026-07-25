# Phase 5 — Backend Gate Record

**Branch:** `agent/phase-5-monetization`  
**Pull Request:** #12  
**Date:** 2026-07-25  
**Status:** Backend lint gate complete; tests and migrations running.

## Lint resolution

The permanent repository workflow runs Backend Ruff from the repository root with:

```text
python -m ruff check \
  backend/app backend/tests backend/alembic/env.py backend/scripts \
  backend/reusable_data_fetcher.py \
  --config backend/pyproject.toml
```

A temporary formatter originally ran from inside `backend/`, which changed Ruff's classification of the installed `sahmi_kasban` package and produced an import layout different from the permanent CI context.

The final correction was applied from the repository root using the exact permanent command. It restored the expected First Party grouping and passed a second no-fix Ruff check.

All temporary diagnostics, result files, and autofix workflows were removed after use.

## Additional hardening completed

- Purchase records receive UUIDs before Wallet Ledger references are created.
- The free subscription remains active as the fallback entitlement.
- Expired paid subscriptions are excluded from active-plan resolution.
- SQLite timestamps are normalized to UTC before Python comparisons.
- The fallback behavior is covered by a dedicated test.
- AdMob stub verification now asserts the specific verification exception rather than a broad exception.

## Next gate

The normal user commit containing this record triggers:

- Backend and Core compilation;
- permanent Ruff checks;
- all Backend and Core tests;
- PostgreSQL 16;
- Alembic upgrade to `0005_monetization`;
- Alembic downgrade to base;
- Alembic rebuild to head;
- unchanged Flutter checks.
