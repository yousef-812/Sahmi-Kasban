# Google Play Release Checklist

Package: `com.sahmikasban.sahmi_kasban_mobile`

## Public Fly URLs

After deploying this branch, use:

- Privacy policy: `https://sahmi-kasban.fly.dev/privacy`
- Terms: `https://sahmi-kasban.fly.dev/terms`
- Financial disclaimer: `https://sahmi-kasban.fly.dev/financial-disclaimer`
- Data safety working sheet: `https://sahmi-kasban.fly.dev/data-safety`
- Financial features working sheet: `https://sahmi-kasban.fly.dev/financial-features`
- Account deletion URL: `https://sahmi-kasban.fly.dev/delete-account`
- Legal index: `https://sahmi-kasban.fly.dev/legal`

The deletion page authenticates the user and calls the same server-authoritative deletion API used by the app. The Android app also exposes deletion under **Account > Edit profile > Delete account permanently**.

## Data safety draft

Declare collection based on the final release and all included SDKs:

- Personal info: email address, name, user ID.
- Financial info: purchase history and subscriptions; no card or bank-account numbers.
- Messages: community discussions, reports, and appeals.
- App activity: analyses, report unlocks, wallet actions, and app interactions needed to provide the service.
- App information and performance: crash logs, diagnostics, and performance metrics when Sentry is enabled.
- Device or other IDs: FCM registration identifiers and AdMob-related identifiers when those features are live.

Security/deletion answers:

- Data is encrypted in transit: yes.
- Users can request deletion: yes.
- Account deletion is available in-app and on the web: yes.
- Verify the current Firebase, AdMob, Google Play Billing, and Sentry SDK disclosures immediately before submission.

## Financial features declaration

The app contains investment-related informational analysis and must not be declared as having no financial features.

Use the closest investment/stocks/information category shown in the current Play Console form and explain:

> Sahmi Kasban provides automated informational analysis for Egyptian Exchange stocks, technical indicators, probabilistic scenarios, and a transparent historical performance ledger. It does not execute trades, connect users to a broker, hold client funds or securities, provide loans, transfer money, offer binary options, or provide personalized licensed investment advice.

No lending, credit, banking, insurance, cryptocurrency, money-transfer, or binary-options features are present.

## Store listing statements

The short and full description must not contain:

- guaranteed-profit language;
- claims that the model is always accurate;
- language suggesting licensed personalized advice;
- misleading claims that data is real-time when it may be delayed;
- performance claims without the visible 7/30-session ledger and data-completeness context.

Include a visible statement that analysis is automated, informational, and does not guarantee profit.

## Submission gates

- Upload a signed production AAB.
- Use the final developer/publisher name consistently in Play Console and the privacy policy.
- Complete App access instructions for reviewer login when needed.
- Complete Content rating, Ads declaration, Data safety, Financial features, and account deletion fields.
- Test subscriptions and one-time products in Internal/Closed Testing.
- Test a signed AdMob SSV callback from the project's own rewarded unit.
- Test live FCM on a physical device.
- Run the **Fly Staging Acceptance** workflow and archive its successful run with the release record.
