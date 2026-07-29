# Phase 11 — Welcome economy, report safety, and stable signing

## Scope

- 5 welcome coins once after verification for accounts created from 2026-07-29.
- Weekly grants: Free 5, Basic 25, Advanced 60, Pro 150 coins.
- Coin packs: 10, 30, 75, and 200 coins.
- Expanded monthly-plan entitlements and comparison allowances.
- Safe Arabic Top 10 report cards with no raw payloads and no locale crash.
- Protected Android signing workflow and certificate fingerprint artifact.

## Safety properties

- Welcome credit is server-authoritative and idempotent by user ID.
- Welcome credit settles inside the email-verification transaction; profile reads remain side-effect free.
- Existing subscriptions are migrated by Alembic revision `0013_economy_v2`.
- Old accounts are not retroactively granted the welcome bonus.
- The first move from an old debug-signed APK to the stable key requires one uninstall; later stable-key APKs update normally.
- Signing files and passwords remain outside Git.

## Release

- Backend migration: `0013_economy_v2`.
- Mobile: `0.8.0+14`.
