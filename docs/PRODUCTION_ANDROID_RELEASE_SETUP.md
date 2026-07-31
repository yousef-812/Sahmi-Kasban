# Production Android release setup

The Android production workflow is intentionally fail-closed for Firebase, AdMob, the production API URL, and the stable signing identity. Sentry is optional; builds remain valid without it, but mobile crash monitoring stays disabled until `SENTRY_MOBILE_DSN` is added.

## Already configured provider secrets

The repository must contain these provider values before the signing script runs:

- `FIREBASE_ANDROID_GOOGLE_SERVICES_JSON`
- `ADMOB_ANDROID_APP_ID`
- `ADMOB_ANDROID_BANNER_ID`
- `ADMOB_ANDROID_NATIVE_ID`
- `ADMOB_ANDROID_INTERSTITIAL_ID`

The AdMob app ID contains `~`. The banner, native, and interstitial unit IDs contain `/`. The Firebase JSON must register Android package `com.sahmikasban.sahmi_kasban_mobile`.

## Prepare the stable Android key

Run from PowerShell on the owner machine after installing Java/keytool and GitHub CLI:

```powershell
./scripts/prepare_production_android_release.ps1 \
  -Repository "yousef-812/Sahmi-Kasban" \
  -ApiBaseUrl "https://sahmi-kasban.fly.dev"
```

Add `-SentryMobileDsn "<mobile-project-dsn>"` later when Sentry is ready.

The script:

1. checks that the Firebase and AdMob repository secrets exist;
2. creates one stable RSA upload keystore outside the repository;
3. records its SHA-256 certificate fingerprint;
4. uploads the keystore, passwords, alias, fingerprint, and production API URL as GitHub Actions secrets;
5. reports missing required secrets without printing secret values.

The generated JKS and `release-key-backup.txt` are permanent release credentials. Keep two encrypted offline backups. Do not regenerate the key after the first installed or Play-distributed release.

To audit names without changing anything:

```powershell
./scripts/prepare_production_android_release.ps1 -CheckOnly
```

## Required final secret set

- `PRODUCTION_API_BASE_URL`
- `FIREBASE_ANDROID_GOOGLE_SERVICES_JSON`
- `ADMOB_ANDROID_APP_ID`
- `ADMOB_ANDROID_BANNER_ID`
- `ADMOB_ANDROID_NATIVE_ID`
- `ADMOB_ANDROID_INTERSTITIAL_ID`
- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`
- `ANDROID_EXPECTED_CERT_SHA256`

Optional:

- `SENTRY_MOBILE_DSN`

## Build store files

Open GitHub Actions, choose **Production Android Release**, run the workflow, and enter exactly:

```text
RELEASE_PRODUCTION
```

The workflow validates Flutter, builds a signed APK and AAB, verifies the real package and certificate fingerprint, and uploads the files with release metadata. The ordinary CI `.ci` APK is only a preview and cannot update the real application.
