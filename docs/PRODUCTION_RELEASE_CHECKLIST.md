# Sahmi Kasban production release checklist

This checklist is the release gate for the public Android application and the production Fly backend.

## Release scope

- Backend configuration: `fly.production.toml`.
- Android workflow: `Production Android Release`.
- Android package: `com.sahmikasban.sahmi_kasban_mobile`.
- Mobile release: `0.9.6+21`.
- Analysis engine: `core-v2.3` with conservative public report wording.
- Database head: `0018_auth_rate_limits`.

Use a separate Fly application and Neon database for production. Create a Neon snapshot before the first public migration.

## Production configuration gate

The production release must provide real, non-test values for:

- production database and migration URLs;
- stable application secret and HTTPS public URL;
- administrator accounts and secure CORS origins;
- SMTP delivery;
- Sentry backend release metadata;
- live Firebase Cloud Messaging credentials;
- live Google Play verification credentials;
- a valid production billing-token encryption key;
- live AdMob rewarded-ad verification and production ad-unit IDs.

The release command in `fly.production.toml` runs the production preflight before Alembic. Missing, mismatched, insecure, or test configuration must stop the rollout.

## Android production gate

The `Production Android Release` workflow requires:

- the production HTTPS API URL;
- Firebase Android configuration;
- production AdMob app, banner, native, and interstitial IDs;
- mobile Sentry configuration;
- the protected Android signing key and expected certificate fingerprint.

Start it manually with the exact production confirmation. It runs Flutter validation, builds signed APK and AAB artifacts, verifies package ID and certificate SHA-256, and publishes release metadata. CI preview APKs use the separate `.ci` package and are not production updates.

## Acceptance tests

### Backend and legal

- `/api/v1/health` returns `ok`.
- `/api/v1/health/ready` returns `ready`, a reachable database, and the compatibility `checks` list.
- Privacy, terms, financial disclaimer, data safety, financial features, and account deletion pages load from the production domain.
- API docs are disabled in production.
- HTTPS responses include HSTS and the configured security headers.

### Authentication and account lifecycle

- Registration delivers the six-digit code.
- Five wrong verification attempts invalidate the code.
- Resend invalidates the previous code.
- Repeated registration, verification, resend, login, forgot-password, and reset-password requests return HTTP 429 with `Retry-After`.
- Refresh rotation, logout, password reset, and password change revoke the expected sessions.
- Account deletion anonymizes the account, revokes sessions, cancels internal entitlements, and removes push-device credentials.
- The app warns that deleting the account does not cancel Google Play automatic renewal.

### Wallet, subscriptions, and ads

- Welcome and weekly grants remain idempotent.
- A Play license-test subscription is verified and acknowledged.
- A coin purchase is verified, consumed, credited once, and cannot be replayed for another user.
- Free users see capped ads; paid users do not see banner, native, or interstitial ads.
- Rewarded-ad server verification rejects invalid signatures, wrong units, expired sessions, and replayed claims.

### Market and reports

- TradingView primary and fallback behavior are healthy.
- Provider failures remain separate from internal failures.
- Daily report generation survives individual ticker failures.
- Public report wording remains analytical and does not present experimental profiles as proven elite opportunities.
- Historical replay runs only on the replay process group and does not block API health.

### Notifications and monitoring

- A physical Android device registers an FCM token.
- Test notifications arrive in foreground and background.
- Invalid device tokens are disabled and deleted-account devices are removed.
- Backend and mobile errors reach the correct Sentry releases without personal data.
- The protected Sentry test and external acceptance/load checks pass.

## Rollout

1. Deploy the production backend first.
2. Confirm `0017_account_token_attempts` and `0018_auth_rate_limits` completed.
3. Run backend acceptance and a real-device closed-test pass.
4. Upload the production AAB to Play Internal testing.
5. Promote to Closed testing only after billing, ads, FCM, account deletion, and update installation pass.
6. Use staged rollout for the first public release.

## Rollback

Record the previous verified Fly image before rollout. Stop the Play rollout and restore the previous application image when health, authentication, wallet integrity, billing verification, or crash thresholds fail. Do not downgrade the database until the downgrade path has passed on a separate Neon branch.

Production launch is approved only when repository CI is green, the real production preflight passes, signed artifacts match the expected package and certificate, live purchase/ad verification passes, physical-device FCM passes, and a database restore point exists.
