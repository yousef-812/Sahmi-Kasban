# Cloud Run staging deployment

This document prepares the first live Sahmi Kasban staging environment without weakening production release gates.

## Target architecture

- Flutter Android application registered with Firebase.
- FastAPI container on Google Cloud Run in a European region.
- Neon PostgreSQL in Frankfurt.
- Firebase Cloud Messaging HTTP v1 through the Cloud Run service identity.
- No downloaded Google service-account private key.

## Fixed identifiers

```text
Firebase project: project-f14e453c-deb8-4a94-b39
Android package: com.sahmikasban.sahmi_kasban_mobile
Cloud Run service account:
sahmi-kasban-backend@project-f14e453c-deb8-4a94-b39.iam.gserviceaccount.com
```

The service account must retain the `Firebase Cloud Messaging API Admin` role. Do not create or download a JSON private key for it.

## Required Secret Manager values

Create these secrets in the same Google Cloud project:

```text
sahmi-database-url
sahmi-migration-database-url
sahmi-secret-key
```

Values:

- `sahmi-database-url`: Neon pooled connection string, converted to the `postgresql+psycopg://` SQLAlchemy scheme.
- `sahmi-migration-database-url`: Neon direct connection string, also using `postgresql+psycopg://`.
- `sahmi-secret-key`: a stable random value containing at least 32 characters.

Never add these values to Git, Flutter, a screenshot, an issue, or a pull-request comment.

## Cloud Run staging environment

Use the following non-secret variables:

```text
APP_ENV=staging
DEBUG=false
LOG_JSON=true
MARKET_TIMEZONE=Africa/Cairo
FCM_DELIVERY_MODE=live
FCM_PROJECT_ID=project-f14e453c-deb8-4a94-b39
FCM_SERVICE_ACCOUNT_JSON=
GOOGLE_PLAY_VERIFICATION_MODE=disabled
ADMOB_SSV_VERIFICATION_MODE=disabled
```

Map Secret Manager values as:

```text
DATABASE_URL=sahmi-database-url:latest
MIGRATION_DATABASE_URL=sahmi-migration-database-url:latest
SECRET_KEY=sahmi-secret-key:latest
```

`FCM_SERVICE_ACCOUNT_JSON` intentionally remains empty on Cloud Run. The Backend obtains short-lived credentials from Application Default Credentials and the attached service identity.

## Container behavior

The Backend container reads Cloud Run's `PORT` variable and defaults to `8080` outside Cloud Run.

Build from the repository root so `backend/Dockerfile` can copy both the analysis package and the Backend package:

```bash
docker build -f backend/Dockerfile -t sahmi-kasban-api:staging .
```

## Database migrations

Run migrations as a one-off controlled task with both database variables available:

```bash
cd /workspace/backend
alembic upgrade head
```

Alembic uses `MIGRATION_DATABASE_URL` when present and otherwise falls back to `DATABASE_URL`. Normal API traffic continues to use the pooled connection.

Do not run Alembic automatically in every Cloud Run instance startup because multiple instances may start concurrently.

## Firebase Android configuration

The repository must never track `mobile/android/app/google-services.json`.

For local Android builds, place the downloaded file at:

```text
mobile/android/app/google-services.json
```

For GitHub Actions, create the repository secret:

```text
FIREBASE_ANDROID_GOOGLE_SERVICES_JSON
```

Paste the complete JSON file as the secret value. CI writes it only for the Flutter build and removes it afterward. Builds without the secret remain valid but do not contain live Firebase Android configuration.

## Staging acceptance test

1. Deploy the Backend with the Cloud Run service account above.
2. Run `alembic upgrade head` once against the direct Neon URL.
3. Confirm the readiness endpoint succeeds.
4. Build Flutter with the real Cloud Run HTTPS URL and `DEMO_MODE=false`.
5. Register and sign in with a real test account.
6. Confirm the user and device registration rows appear in Neon.
7. Send a notification from the administrator interface.
8. Confirm both the Android push and the in-app inbox entry arrive.
9. Confirm no service-account JSON, Neon password, or application secret appears in logs or artifacts.

## Production boundary

Staging may keep Google Play verification, AdMob SSV, SMTP delivery, and Sentry disabled while those integrations are being accepted. `APP_ENV=production` remains strict and refuses to start until the production release integrations are configured.
