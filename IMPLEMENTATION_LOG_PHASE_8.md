# Phase 8 — Administration Dashboard and Notifications

> Branch: `agent/phase-8-admin-notifications`  
> Pull request: #17  
> Merge commit: `1cd87a940e6cf317ee71572b9487827ff4aef8fe`  
> Updated: 2026-07-26

## Administration foundation

- The existing Phase 6 community moderation, appeals, account blocking, and audit trail remain protected by `ADMIN_EMAILS`.
- Phase 8 adds a protected operational overview, user directory, runtime settings, provider health history, broadcast notifications, and a consolidated audit feed.
- The Flutter profile receives an `is_admin` flag computed by the Backend. The `/admin` route is hidden and guarded for non-administrators.

## Runtime settings

The allowlisted settings table stores only validated operational values. Arbitrary configuration keys and secrets cannot be written through the API.

Current settings cover:

- fresh stock-analysis price;
- daily Top 10 report unlock price;
- rewarded-ad points, Cairo daily limit, and cooldown;
- community short-window duration and limit;
- community 24-hour limit;
- notification enable/disable switch.

Every update creates an immutable `CommunityAdminEvent` containing the old and new values. Analysis pricing, report pricing, rewarded-ad policy, and community rate limits consume the runtime values on the server.

## Notifications and Push

- Notifications are stored per user before any Push attempt.
- Read state is server-authoritative and supports one notification or all notifications.
- Device tokens are stored as SHA-256 hashes plus encrypted token values derived from the application secret.
- FCM delivery supports `disabled`, `stub`, and `live` modes.
- Live mode uses Firebase Cloud Messaging HTTP v1 with service-account credentials supplied only through environment configuration.
- Every device delivery records sent, failed, or skipped status and the provider message/error identifier.
- Flutter initializes Firebase defensively, requests permission, registers a device token when available, and continues normally when Firebase project files are not configured.

## Deferred live Push activation

- No live Firebase Cloud Messaging Push notification has been configured or sent yet.
- The currently completed scope is the in-app notification inbox, encrypted device-token storage, delivery audit, and the `disabled`/`stub` delivery paths.
- `live` mode remains inactive and must not be treated as production-verified.
- Live Push activation is intentionally deferred to a later pre-release task.
- That later task must add the Firebase project files, configure `FCM_PROJECT_ID` and `FCM_SERVICE_ACCOUNT_JSON` as deployment secrets, register a physical device, send a real test notification, and verify the delivery audit end to end.

## Provider monitoring

The administrator can run an explicit health probe for:

- the configured market-data fallback chain using a bounded COMI history request;
- the configured AI provider using a minimal deterministic prompt.

Each probe stores provider, status, latency, observation time, and safe diagnostic details. Provider failures are recorded instead of causing the administration endpoint to fail.

## Flutter administration dashboard

The dashboard provides:

- product and moderation metrics;
- provider health and manual probes;
- pending discussion approval/rejection;
- user list and block/unblock actions;
- validated runtime setting edits;
- broadcast announcements to active users;
- consolidated administrator audit events.

## Validation status

- Flutter analysis completed with no findings after adding mounted guards around dialog-driven administrator actions.
- Backend imports use the CI-compatible internal package grouping for both `app` and `sahmi_kasban`.
- The first complete validation gate passed on Workflow `30185904045`.
- The final merge gate passed on Workflow `30186148102`: repository lint, Backend/Core/PostgreSQL tests, Alembic upgrade/downgrade/rebuild, Flutter format/analyze/tests, and Android debug APK all succeeded.
- PR #17 was merged into `main` with squash commit `1cd87a940e6cf317ee71572b9487827ff4aef8fe`.