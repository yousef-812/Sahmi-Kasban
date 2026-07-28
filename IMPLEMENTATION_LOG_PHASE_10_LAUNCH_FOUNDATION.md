# Phase 10 Launch Foundation

Date: 2026-07-28

## Legal and Google Play

- Public Arabic RTL pages are served by the existing Fly FastAPI application.
- Added privacy policy, terms, financial disclaimer, Data safety working sheet, Financial features working sheet, legal index, and authenticated web account deletion.
- Added an in-app account deletion path requiring the current password.
- Added a Google Play release checklist with exact Fly URLs and declaration guidance.

## Reliability and operations

- Added external GitHub-hosted Fly acceptance/load workflow.
- Added a protected PII-free Sentry delivery probe for administrators.
- Added Sentry release and sampling defaults; the DSN remains a platform secret.
- Added Neon snapshot/PITR, portable backup, restore-drill, and Fly rollback procedures.
- Added a PowerShell Fly image rollback helper with post-rollback health verification.
- Local database dumps are ignored by Git.

## Product decisions

- Locked TradingView primary/yfinance fallback behavior and cache semantics.
- Locked Monday Cairo weekly grants and added an always-on idempotent weekly-grant scheduler.
- Locked launch coin/subscription amounts and proposed Egypt Play prices.
- Locked analysis lifetime to finalized market snapshot + engine version.
- Locked history limits and removed watchlist promises from the first release.
- Locked community no-edit policy for frozen predictions.
- Locked informational-only financial positioning and Egypt launch jurisdiction language.

## Live-testing fix included

- Wallet history HTTP requests were succeeding, but the screen crashed while formatting Arabic dates because locale data was not initialized.
- Removed locale-dependent `DateFormat` usage from the wallet ledger.
- Added safe Arabic date/status/transaction labels and a widget regression test.

## Release version

- Android/Flutter: `0.7.0+13`.
- Backend Sentry release label: `sahmi-kasban-backend@0.7.0`.
