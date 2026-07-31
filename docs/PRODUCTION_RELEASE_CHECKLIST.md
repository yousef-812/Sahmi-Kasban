# Sahmi Kasban production release checklist

This checklist is the release gate for the public Android application and the production Fly backend. Staging success is required but is not a substitute for completing the production-only integrations below.

## 1. Release scope

- Backend configuration: `fly.production.toml`.
- Android workflow: `Production Android Release`.
- Android package: `com.sahmikasban.sahmi_kasban_mobile`.
- Mobile release: `0.9.6+21`.
- Analysis engine: `core-v2.3` with conservative public report wording.
- Database head: `0016_auth_rate_limits`.

Do not reuse the staging Fly app or staging database as the public production environment.

## 2. Production infrastructure

Before the first deployment:

1. Create a separate Fly application for production.
2. Create or select the production Neon database in Frankfurt.
3. Enable Neon restore/PITR support appropriate for the plan.
4. Create a manual snapshot immediately before the first public migration.
5. Keep the replay worker and API process groups defined in `fly.production.toml`.
6. Keep at least one API Machine running to avoid user-facing cold starts.

Deploy explicitly with the production config:

```powershell
fly deploy -a <production-app> -c fly.production.toml
```

The release command runs production preflight validation before Alembic. A missing or test integration must stop the rollout.

## 3. Required Fly secrets and production values

Store real values in Fly Secrets. Never commit them or place them in screenshots, logs, issue comments, or ordinary repository files.

### Core and database

- `DATABASE_URL`: pooled production Neon URL.
- `MIGRATION_DATABASE_URL`: direct production Neon URL.
- `SECRET_KEY`: stable random application secret, at least 32 characters.
- `APP_PUBLIC_URL`: absolute production HTTPS URL.
- `ADMIN_EMAILS`: comma-separated production administrator accounts.
- `CORS_ORIGINS`: empty when no browser client exists, otherwise explicit HTTPS origins only.

### Email

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`: deliverable non-local sender address.
- `SMTP_USE_TLS=true`

### AI and observability

- `GROQ_API_KEYS` or the approved alternative provider credentials.
- `SENTRY_DSN`
- `SENTRY_RELEASE`: immutable release identifier, preferably tied to the deployed commit.

### Firebase Cloud Messaging

- `FCM_PROJECT_ID`
- `FCM_SERVICE_ACCOUNT_JSON`: JSON secret, or use `GOOGLE_APPLICATION_CREDENTIALS` with a mounted readable JSON file.
- `FCM_DELIVERY_MODE=live`

The Firebase project ID must match the service-account project.

### Google Play billing

- `GOOGLE_PLAY_PACKAGE_NAME=com.sahmikasban.sahmi_kasban_mobile`
- `GOOGLE_PLAY_VERIFICATION_MODE=live`
- `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`: JSON text accepted by the backend verifier.
- `BILLING_TOKEN_ENCRYPTION_KEY`: a valid Fernet key generated specifically for production.

Example local generation; copy only the output into the secret vault:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Never rotate this key without a migration plan for already encrypted purchase tokens.

### AdMob rewarded SSV

- `ADMOB_SSV_VERIFICATION_MODE=live`
- `ADMOB_ANDROID_REWARDED_AD_UNIT_ID`: production rewarded unit.
- `ADMOB_IOS_REWARDED_AD_UNIT_ID`: production rewarded unit when iOS ships.
- `ADMOB_REWARD_ITEM`

Production must not contain Google test publisher ID `3940256099942544`.

## 4. Required GitHub Actions secrets for Android

The `Production Android Release` workflow refuses to run without all of these:

- `PRODUCTION_API_BASE_URL`
- `FIREBASE_ANDROID_GOOGLE_SERVICES_JSON`
- `ADMOB_ANDROID_APP_ID`
- `ADMOB_ANDROID_BANNER_ID`
- `ADMOB_ANDROID_NATIVE_ID`
- `ADMOB_ANDROID_INTERSTITIAL_ID`
- `SENTRY_MOBILE_DSN`
- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`
- `ANDROID_EXPECTED_CERT_SHA256`

Start the workflow manually and enter exactly `RELEASE_PRODUCTION`. It builds both APK and AAB, rejects HTTP/test IDs, verifies the package and certificate, and uploads release metadata.

The normal CI preview APK uses a separate `.ci` package and is never a production update.

## 5. Google Play Console setup

Before closed testing:

1. Create every subscription and coin product using the exact server catalog product IDs.
2. Activate products and configure prices in EGP.
3. Grant the backend service account only the permissions required to verify and acknowledge purchases.
4. Add license tester accounts.
5. Upload the generated production AAB to Internal testing first.
6. Verify the certificate fingerprint against `production-release-metadata.txt`.
7. Complete Data safety and Financial features declarations from the published legal pages.
8. Set the privacy-policy and account-deletion URLs to the production domain.

Account deletion removes access and stored push credentials. Users with Play subscriptions must still cancel automatic renewal in Google Play; the app warns them before deletion.

## 6. Acceptance tests before public rollout

### Backend and legal

- `/api/v1/health` returns `ok`.
- `/api/v1/health/ready` returns `ready` and `database=reachable`.
- `/privacy`, `/terms`, `/financial-disclaimer`, `/data-safety`, `/financial-features`, and `/delete-account` return Arabic RTL pages.
- Production API docs and OpenAPI endpoints are disabled.
- HTTPS responses include HSTS and the configured security headers.

### Authentication and account lifecycle

- Register a new account and receive the six-digit code.
- Five wrong verification attempts invalidate the code.
- Resend creates a new code and invalidates the previous one.
- Login, refresh-token rotation, logout, password reset, and password change all revoke the expected sessions.
- Repeated authentication requests return HTTP 429 with `Retry-After`.
- Account deletion anonymizes the account, revokes sessions, cancels internal entitlements, and deletes push-device credentials.

### Wallet, subscriptions, and ads

- Welcome bonus is granted once after verification.
- Weekly grants are idempotent for the Cairo week.
- A license-test subscription is verified by the backend and acknowledged by Google Play.
- A coin purchase is verified, consumed, and credited once.
- Replaying the same purchase token is idempotent and cannot credit another user.
- Free users see banner/native/interstitial ads according to caps.
- Paid users see no banner/native/interstitial ads.
- Rewarded SSV credits the server-defined reward once and rejects replay, expired sessions, wrong units, and invalid signatures.

### Market and reports

- TradingView primary and fallback behavior are healthy.
- Failed symbols are reported separately from internal failures.
- Daily report generation survives individual ticker failures.
- Public report wording remains analytical and does not call experimental balanced/aggressive profiles proven elite opportunities.
- Historical replay runs only on the replay process group and does not block API health.

### Notifications and monitoring

- Android registers an FCM token after permission.
- A test notification arrives in foreground and background.
- Invalid device tokens become disabled or are removed on account deletion.
- Backend and mobile errors arrive in the correct Sentry release without PII or screenshots.
- Run the protected Sentry test endpoint as an administrator.
- Run the external acceptance/load workflow and keep P95 within the configured gate.

## 7. Rollout and rollback

1. Deploy production backend first.
2. Confirm migrations `0015_account_token_attempts` and `0016_auth_rate_limits` completed.
3. Run backend acceptance and one real-device closed-test pass.
4. Upload the production AAB to Internal testing.
5. Promote to Closed testing only after billing, ads, FCM, deletion, and update installation pass.
6. Use staged Play rollout for the first public release.

Rollback when health checks, authentication, wallet integrity, billing verification, or crash rate fail the acceptance threshold:

- stop Play rollout or roll back to the previous Play release;
- deploy the previous verified Fly image;
- do not downgrade the database until the downgrade path has been tested on a separate Neon branch;
- preserve audit and Sentry evidence for the incident review.

## 8. Release decision

Production launch is approved only when:

- repository CI is fully green;
- the production preflight command passes against the real secret set;
- the production backend acceptance suite passes;
- the signed AAB certificate and package match the expected values;
- Play license-test purchases and AdMob SSV pass;
- Firebase background delivery passes on a physical Android device;
- a Neon snapshot exists and the rollback image is recorded.
