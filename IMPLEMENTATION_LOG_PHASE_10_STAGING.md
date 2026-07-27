# Phase 10 — Firebase, Neon, and Cloud Run staging preparation

## Scope

This package prepares the first real staging deployment while keeping production release gates strict.

## Android and Firebase

- Registered Android package: `com.sahmikasban.sahmi_kasban_mobile`.
- Added Google Services Gradle plugin version `4.5.0`.
- Applied the plugin only when `google-services.json` exists so ordinary CI and disconnected preview builds remain valid.
- Ignored the local Firebase config file explicitly.
- Added optional GitHub Actions injection through `FIREBASE_ANDROID_GOOGLE_SERVICES_JSON` without tracking the file.

## Backend and FCM

- Added Application Default Credentials fallback for FCM HTTP v1.
- Retained support for explicit service-account JSON outside Google Cloud.
- Allowed Cloud Run to use the attached `sahmi-kasban-backend` service identity without a downloaded private key.
- Added regression coverage for ADC project discovery and Firebase Messaging scope selection.

## Neon database

- Added `MIGRATION_DATABASE_URL` for the direct Neon connection.
- Kept `DATABASE_URL` for pooled application traffic.
- Updated Alembic to prefer the direct migration URL and fall back safely when it is absent.

## Staging and production boundaries

- Staging requires a long stable secret and PostgreSQL.
- Staging may keep SMTP, Sentry, Google Play verification, and AdMob SSV disabled during acceptance work.
- Production continues to reject startup unless all release integrations and real AdMob identifiers are configured.

## Cloud Run container

- Changed the container to use Cloud Run's `PORT` variable.
- Defaulted local container execution to port `8080`.
- Documented Secret Manager mappings, migration execution, Firebase configuration, and the complete staging acceptance sequence.

## Validation target

The pull request must pass:

- repository lint and secret scanning;
- Backend and PostgreSQL tests;
- Alembic upgrade/downgrade/rebuild checks;
- Flutter formatting, analysis, and tests;
- Android debug APK build both with and without optional Firebase configuration.

Live acceptance remains external to CI and requires the user's Neon secrets, Cloud Run deployment, real Android device token, and Firebase project permissions.
