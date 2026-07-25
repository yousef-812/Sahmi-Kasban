# Phase 6 Flutter Community Implementation Log

> Branch: `agent/phase-6-community-core`  
> Pull request: Draft PR #15  
> Updated: 2026-07-26

## Scope implemented

- Added typed Flutter models for discussions, authors, submissions, reports, mutes, appeals, and paginated responses.
- Added a dedicated community repository using the existing authenticated `ApiClient` and refresh-token flow.
- Added parsing for FastAPI validation errors and `Retry-After` on HTTP 429 responses.
- Added Riverpod providers for the public feed, ticker filter, discussion details, My Discussions, and My Appeals.
- Added an Arabic RTL Community feed with pull-to-refresh and ticker filtering.
- Added discussion details with frozen prediction, moderation information for the owner, reporting, muting, unmuting, and appeal submission.
- Added discussion creation with EGX instrument selection, a stable submission key for retries, a 0.5-coin hold warning, and wallet/profile refresh after submission.
- Added My Discussions and My Appeals screens with lifecycle and resolution states.
- Added Community as a fifth dashboard destination and registered all community routes in `GoRouter`.
- Added model, repository, HTTP error, pagination, and widget coverage.

## Server-authoritative guarantees preserved

- Flutter never edits wallet balances locally.
- The same submission key remains stable throughout one form attempt.
- The server remains responsible for holds, confirmation, release, moderation, rejection, and appeal charging.
- Wallet and profile providers are refreshed after a submission that can change the balance.

## Validation gate

The Flutter formatter was applied to `mobile/lib` and `mobile/test` after navigation wiring. This documentation commit intentionally triggers the complete repository workflow on a normal user-authored commit. PR #15 must remain Draft until repository lint, backend/PostgreSQL/Alembic checks, Flutter analyze/tests, and Android debug APK all succeed on the latest code.
