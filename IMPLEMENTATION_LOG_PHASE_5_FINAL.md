# Sahmi Kasban — Phase 5 Finalization Record

## Status

**Phase:** Ads, rewarded coins, subscriptions, and coin packs  
**Branch:** `agent/phase-5-monetization`  
**Pull Request:** #12  
**Roadmap version:** 1.3  
**Status:** Code complete and ready for final repository validation.

## Delivered Backend functionality

- Server-owned catalog for Free, Basic, Advanced, and Pro plans.
- Server-owned catalog for four Google Play coin packs.
- Reversible Alembic migration `0005_monetization`.
- Encrypted purchase-token storage with a separate unique SHA-256 hash.
- Idempotent Google Play purchase processing.
- Purchase-token ownership enforcement across users and products.
- Subscription activation from server catalog benefits only.
- Free-plan fallback after paid-plan expiry.
- Rewarded-ad sessions with short-lived Backend-issued `custom_data`.
- AdMob SSV signature-verification foundation.
- Fixed 75-point rewarded-ad grant, four-per-Cairo-day limit, and cooldown.
- Unique AdMob transaction, rewarded session, and Wallet Ledger protection.
- Development/Test-only authenticated SSV simulation.
- Production and Staging rejection of Stub verification modes and sample rewarded IDs.
- Weekly grant job using the active plan's weekly allocation.
- Weekly grants verified for 300, 1,000, 1,500, and 5,000 points.
- Weekly grant idempotency and expired-paid-plan fallback tests.

## Delivered Flutter functionality

- `google_mobile_ads` integration.
- `in_app_purchase` integration for Android Google Play.
- Arabic plans and coin-pack screen.
- Store prices loaded from Google Play `ProductDetails`.
- Pending, cancelled, restored, purchased, and error-state handling.
- Server purchase-token verification before entitlement completion.
- Rewarded test-ad flow using Backend-issued `custom_data`.
- Wallet/status refresh after verified rewarded grant.
- Banner test ad for ad-enabled plans only.
- Paid plans remove the banner and rewarded-ad entry points.
- Build-time AdMob application and banner identifiers.
- Android debug APK build gate in repository CI.

## Verified test behavior

- A completed Stub Google Play coin purchase credits once.
- Repeating the same purchase token is idempotent.
- A token cannot be moved to another user.
- Subscription products activate the expected server plan.
- Expired paid subscriptions fall back to Free.
- A rewarded Test/Stub transaction credits exactly 75 points once.
- Repeating the same rewarded transaction does not duplicate value.
- Four daily rewards are enforced server-side.
- Paid plans cannot request rewarded-ad sessions.
- Weekly distributions match every plan and do not repeat in the same Cairo week.
- Repository lint, Flutter format/analyze/tests, Backend/Core tests, PostgreSQL, Alembic lifecycle, and Android APK compilation have all passed during Phase 5 development.

## Mandatory live-test warning

> [!WARNING]
> **Real monetization has not been tested yet.** No real purchase has been completed from a signed build installed through Google Play Internal Testing, and no live signed AdMob Server-Side Verification callback has been received from this project's own rewarded-ad unit. Google sample ads, Stub verification, automated tests, and debug APK compilation prove the repository code paths only. They do not prove the external Play Console products, service-account permissions, acknowledgement/consumption behavior, AdMob app/ad-unit setup, or callback registration. Production release remains blocked until the acceptance procedure in `docs/MONETIZATION_SETUP.md` is completed and evidence is recorded.

## Production acceptance still required

1. Create and activate the exact subscriptions and coin products in Play Console.
2. Configure the Google Play service account and production Backend secrets.
3. Upload a signed AAB to Internal Testing and install it from Google Play.
4. Complete real test purchases, pending purchases, restoration, cancellation, expiry, and refund scenarios.
5. Create the project's own AdMob app and rewarded/banner units.
6. Register the live SSV callback and receive a valid Google-signed callback.
7. Confirm that duplicate purchase tokens and AdMob transaction IDs do not duplicate value in the live environment.
8. Record the evidence before allowing a production release.

## Primary references

```text
ROADMAP.md
IMPLEMENTATION_LOG_PHASE_5.md
IMPLEMENTATION_LOG_PHASE_5_BACKEND_GATE.md
IMPLEMENTATION_LOG_PHASE_5_FLUTTER.md
docs/MONETIZATION_SETUP.md
```
