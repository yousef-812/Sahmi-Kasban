# Sahmi Kasban — Monetization Setup

This document separates the implemented application behavior from the external Google Play and AdMob setup required before a production release.

> [!WARNING]
> **Live monetization has not been tested yet.** No real purchase has been completed through a Google Play Internal Testing build, and no real signed AdMob Server-Side Verification callback has been received from this project's own AdMob rewarded ad unit. Repository tests, Stub mode, Google sample ads, and a successful debug APK build verify the code paths only; they do **not** prove that the live Play Console, service-account permissions, product configuration, billing acknowledgement/consumption, AdMob app/ad-unit configuration, or SSV callback registration are correct. Production release is blocked until the acceptance procedure in section 9 is completed and its evidence is recorded.

## 1. Server-authoritative rules

The mobile application is never the source of truth for money, coins, subscriptions, or rewarded-ad grants.

- A Google Play purchase changes the account only after the Backend verifies the Android purchase token.
- A rewarded ad changes the wallet only after a verified AdMob SSV callback creates a unique Wallet Ledger entry.
- The same purchase token, AdMob transaction ID, rewarded session, or Wallet transaction cannot grant value twice.
- Pending, cancelled, expired, unknown, or unverified purchases grant nothing.
- Product IDs, plan benefits, coin amounts, reward amount, daily limits, and cooldowns come from the server.

## 2. Google Play package and products

Android application ID and Backend package name:

```text
com.sahmikasban.sahmi_kasban_mobile
```

Create the following products in Google Play Console using the exact IDs.

### Subscriptions

```text
sahmi_basic_monthly
sahmi_advanced_monthly
sahmi_pro_monthly
```

Create and activate a monthly base plan for each subscription. Prices and currencies belong in Google Play Console and are displayed from `ProductDetails`; they are not hardcoded in Flutter.

### One-time consumable products

```text
sahmi_coins_5
sahmi_coins_15
sahmi_coins_40
sahmi_coins_100
```

Server grants:

| Product | Points | Coins |
|---|---:|---:|
| `sahmi_coins_5` | 500 | 5.00 |
| `sahmi_coins_15` | 1500 | 15.00 |
| `sahmi_coins_40` | 4000 | 40.00 |
| `sahmi_coins_100` | 10000 | 100.00 |

Do not change a grant by editing Flutter. Update the server catalog, migration-safe operational configuration, and product documentation together.

## 3. Google Play Developer API

Create a Google Cloud service account, link it to Play Console, and grant the minimum permissions needed to read subscriptions and in-app purchases and manage acknowledgement/consumption.

Store the complete service-account JSON only in the Backend secret store. Never commit it and never place it in Flutter.

Production Backend variables:

```text
GOOGLE_PLAY_PACKAGE_NAME=com.sahmikasban.sahmi_kasban_mobile
GOOGLE_PLAY_VERIFICATION_MODE=live
GOOGLE_PLAY_SERVICE_ACCOUNT_JSON={...single-line service account JSON...}
BILLING_TOKEN_ENCRYPTION_KEY=<Fernet key>
```

Generate a Fernet key locally:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

The key encrypts purchase tokens at rest. SHA-256 hashes are stored separately for uniqueness and lookup.

## 4. AdMob application and ad units

Create the production Android application in AdMob with the same package name. Create at least:

- Android rewarded ad unit.
- Android banner ad unit.
- iOS rewarded and banner ad units only if an iOS release is planned.

Backend production variables:

```text
ADMOB_SSV_VERIFICATION_MODE=live
ADMOB_ANDROID_REWARDED_AD_UNIT_ID=<real rewarded ad unit>
ADMOB_IOS_REWARDED_AD_UNIT_ID=<real rewarded ad unit if used>
ADMOB_REWARD_ITEM=coins
AD_REWARD_POINTS=75
AD_REWARD_DAILY_LIMIT=4
AD_REWARD_COOLDOWN_SECONDS=900
AD_REWARD_SESSION_MINUTES=15
```

Configure the rewarded ad unit's server-side verification callback URL as:

```text
https://<backend-host>/api/v1/monetization/admob/ssv
```

Flutter attaches Backend-issued random data using `ServerSideVerificationOptions.customData`. AdMob returns it as `custom_data`; the Backend verifies the ECDSA signature against Google's rotating keys before looking up the session and crediting the wallet.

## 5. Development and test ads

Development uses Google sample application and ad-unit IDs. They are safe for test traffic but must not be shipped as production configuration.

Rewarded-session development requires explicit Stub mode:

```text
APP_ENV=development
ADMOB_SSV_VERIFICATION_MODE=stub
GOOGLE_PLAY_VERIFICATION_MODE=stub
```

Google sample rewarded ads cannot send SSV callbacks to this project's Backend. Therefore, Development/Test plus Stub mode exposes a hidden authenticated simulation endpoint after the sample ad completes. The endpoint returns 404 in Staging and Production and cannot be enabled there because configuration validation requires `live` mode.

Stub purchase token format used only in automated/local tests:

```text
stub-purchased:<test-order-id>:<unique-value>
```

Do not enable Stub mode on any public production environment.

## 6. Android build

The Android manifest receives the AdMob application ID from the build environment. If the variable is absent, the official sample app ID is used.

Production example:

```bash
cd mobile
export ADMOB_ANDROID_APP_ID='ca-app-pub-REAL~APP'
flutter build appbundle --release \
  --dart-define=API_BASE_URL=https://api.example.com \
  --dart-define=ADMOB_ANDROID_BANNER_ID=ca-app-pub-REAL/BANNER
```

The rewarded ad-unit ID is returned by the Backend, not embedded in Flutter.

Before uploading, confirm that the generated manifest and release build do not contain Google's sample publisher ID `3940256099942544`.

## 7. iOS build

Phase 5 digital purchases are Google Play/Android only. The iOS project contains AdMob support for future use.

`Info.plist` reads:

```text
$(ADMOB_IOS_APP_ID)
```

Debug and Release xcconfig files currently default to Google's sample app ID. Override the Xcode build setting and Flutter banner define for a production archive:

```text
ADMOB_IOS_APP_ID=ca-app-pub-REAL~APP
ADMOB_IOS_BANNER_ID=ca-app-pub-REAL/BANNER
```

## 8. Required Backend production gates

Production configuration intentionally fails startup unless all conditions are true:

- `APP_ENV` is production or staging with a strong `SECRET_KEY`.
- PostgreSQL and SMTP are configured.
- Google Play verification mode is `live`.
- Service-account JSON is present.
- Purchase-token encryption key is present.
- AdMob SSV mode is `live`.
- Rewarded ad units are not Google sample IDs.

The Flutter release pipeline must separately verify native AdMob app IDs and banner IDs because they are build-time mobile values.

## 9. Internal testing procedure

> [!IMPORTANT]
> This procedure is still pending. Phase 5 must not be described as live-payment-tested until every item below is completed using the real Play Console and AdMob configuration and the evidence is appended to the implementation log.

1. Create and activate all Play products.
2. Upload a signed Android App Bundle to an Internal Testing track.
3. Add license testers and install the build through Google Play.
4. Use a real tester purchase and verify that the Backend records one `billing_purchases` row.
5. Repeat the same token and confirm that the wallet or subscription does not change again.
6. Test a pending payment method and confirm that no entitlement is granted.
7. Configure AdMob SSV and use a real test device with the project's own rewarded ad unit.
8. Confirm one `rewarded_ad_claims` row and one Wallet Ledger entry per transaction ID.
9. Verify the daily limit, cooldown, paid-plan ad removal, and free-plan fallback after subscription expiry.
10. Test refund, cancellation, grace-period, and expiry synchronization before public release.

## 10. External gates not reproducible in repository CI

Repository CI verifies models, migrations, idempotency, encryption, limits, Flutter flows, static analysis, tests, and Android debug compilation. It cannot prove a live purchase or signed AdMob callback without:

- a configured Play Console application and active products;
- service-account access to the live application;
- a signed build installed through a Play testing track;
- real AdMob app/ad-unit configuration and SSV callback registration.

**Current acceptance status: NOT TESTED LIVE.** These remain release-environment acceptance tests, not reasons to trust the client. Production verification remains disabled until the required secrets and live modes are explicitly configured.