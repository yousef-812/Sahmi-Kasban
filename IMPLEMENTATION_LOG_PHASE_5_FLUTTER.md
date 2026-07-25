# Phase 5 — Flutter Monetization Integration Record

**Branch:** `agent/phase-5-monetization`  
**Pull Request:** #12  
**Date:** 2026-07-25  
**Status:** Flutter integration implemented; permanent Analyze/Test gate running.

## Packages

```text
google_mobile_ads: 9.0.0
in_app_purchase: 3.3.0
Dart SDK: >=3.10.0 <4.0.0
Android minSdk: 24
```

`pubspec.lock` was regenerated with Flutter Stable and all Dart files were formatted with the Dart formatter bundled with that same SDK.

## Rewarded ads

- Flutter requests a short-lived rewarded-ad session from the Backend.
- The Backend chooses the ad-unit ID and returns random `custom_data`.
- Flutter attaches `custom_data` using `ServerSideVerificationOptions` before displaying the ad.
- `onUserEarnedReward` only indicates that the ad completed locally; it does not credit the wallet.
- In live mode the client polls the Backend until signed AdMob SSV creates the Wallet Ledger entry.
- Official Google demo ad units are used during development.
- Since demo ad units cannot send SSV to this project's callback, Development/Test with explicit Stub mode uses a hidden authenticated simulation route.
- The simulation route is unavailable in Staging/Production and returns 404 outside Development/Test + Stub mode.
- The server remains authoritative for the fixed 75-point reward, four-per-day limit, cooldown, and duplicate prevention.

## Google Play Billing

- Flutter queries only product IDs returned by the server catalog.
- Prices are rendered from Google Play `ProductDetails`; no prices are hardcoded in the app.
- Purchase updates are consumed from `purchaseStream`.
- Pending purchases remain pending and grant nothing.
- Android `serverVerificationData` is sent to the Backend as the purchase token.
- Flutter calls `completePurchase` only after the Backend confirms the entitlement.
- Coin packs use a consumable purchase request with client auto-consumption disabled.
- Subscriptions use the non-consumable purchase request path supported by the Flutter plugin.
- Restore purchases replays purchase details through the same Backend verification path.
- iOS ads are configured, but digital purchases in Phase 5 remain Google Play/Android only as defined by the roadmap.

## User interface

A new Arabic screen at `/monetization` includes:

- current plan and weekly allocation;
- rewarded-ad availability and daily remaining count;
- Free, Basic, Advanced, and Pro cards;
- live Google Play prices when products are configured;
- four server-defined coin packs;
- restore-purchases action;
- clear server-verification and duplicate-prevention notice.

The Wallet tab now links directly to this screen.

## Native configuration

- Android Manifest contains the official Google sample AdMob application ID for development.
- iOS Info.plist contains the official Google sample AdMob application ID for development.
- Production Backend configuration rejects Google demo ad-unit IDs.
- Android application ID and Backend package name both use:

```text
com.sahmikasban.sahmi_kasban_mobile
```

## Tests added

- Flutter catalog parses only server-defined store product IDs.
- Coin packs and subscriptions are classified correctly.
- Rewarded session preserves `test_mode` and Backend-issued custom data.
- Purchase response keeps the Backend entitlement decision and resulting balance.
- Backend rejects rewarded sessions when SSV verification is disabled.
- Production settings reject Stub verifiers and Google demo IDs.

## Current gate

Commit `b90318b67cd2c85edcef8f0935aefd850bf20537` contains the formatter output. This normal documentation commit triggers the permanent workflow against the formatted source so Flutter Analyze and all tests can report real integration findings.
