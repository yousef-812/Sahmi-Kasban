# Phase 7 — Prediction Evaluation and Rewards

> Branch: `agent/phase-7-prediction-evaluation`  
> Pull request: #16  
> Updated: 2026-07-26

## Product behavior

- Verification eligibility is derived on the server from the publication time, the selected period, the EGX Sunday–Thursday calendar, configured holidays, and `Africa/Cairo` time.
- `next_session`, `week`, and `month` resolve to 1, 5, and 20 completed trading sessions respectively.
- Verification becomes available after 5:00 PM Cairo time on the final target session.
- Missing final candles block verification with a retryable service response instead of creating a partial result.

## Deterministic scoring

The reward decision is calculated without trusting AI output:

- direction: 40%;
- target price: 30%;
- timing and movement path: 20%;
- prediction specificity: 10%.

Reward tiers are fixed in Backend code:

- below 40%: 0 points;
- 40% to below 60%: 50 points (0.5 coin);
- 60% to below 80%: 100 points (1 coin);
- 80% or more with a specific target, deadline, or path: 200 points (2 coins).

A generic direction-only prediction cannot receive the `very_strong` level.

## Transaction integrity

- The discussion row is locked before finalization.
- Each discussion has one unique `PredictionVerification` record.
- Reward transaction IDs use `prediction:{discussion_id}:reward`.
- Wallet rewards use the immutable Wallet Ledger and are safe under retries.
- Repeated verification requests return the stored result without fetching market data or crediting the wallet again.

## AI role

- AI receives only the frozen prediction and calculated market outcome.
- AI produces a user-facing explanation and claim comparison.
- AI-proposed level or reward values are ignored.
- If the provider fails, a deterministic Arabic explanation is stored and the fixed score/reward remains unchanged.

## API

```text
GET  /api/v1/community/discussions/{discussion_id}/verification
POST /api/v1/community/discussions/{discussion_id}/verification
GET  /api/v1/community/predictions/stats/mine
```

## Flutter

- Published owner discussions show one of four server states: waiting, eligible, verified, or unavailable.
- The verification button appears only for the eligible state.
- Successful verification refreshes the wallet, profile, My Discussions, and prediction statistics.
- The result card displays the fixed score, strength, reward, verification time, and explanation.
- My Discussions includes verified count, accepted percentage, average score, and total rewards.

## Tests

Coverage includes:

- Cairo/EGX session-window resolution;
- incomplete final-candle rejection;
- fixed scoring components and generic-prediction cap;
- early-verification rejection;
- exactly-once verification and reward credit;
- AI provider fallback;
- API status, execution, repeat request, and statistics;
- Flutter model, repository, waiting, eligible, and verified UI states.

## Validation checkpoints

Workflow `30183634855` passed the complete Phase 7 gate:

- repository lint;
- Backend/Core/PostgreSQL tests and Alembic upgrade/downgrade/rebuild;
- Flutter formatting and static analysis;
- all Flutter tests;
- Android debug APK build.

`ROADMAP.md` is now version 1.6, marks Phase 7 complete on PR #16, and identifies Phase 8 — administration dashboard and notifications — as the next phase.

This normal user-authored documentation commit intentionally starts the final complete workflow on the exact PR head. PR #16 must remain Draft until that final run is fully green.
