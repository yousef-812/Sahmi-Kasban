# Administration Operations and Notifications

Phase 8 adds a protected operational administration surface to Sahmi Kasban. All administration endpoints require an authenticated active account whose normalized email is present in `ADMIN_EMAILS`.

## Runtime configuration

The administration API exposes only an allowlist of validated product settings. It does not expose environment secrets or permit arbitrary keys.

```text
GET /api/v1/admin/operations/settings
PUT /api/v1/admin/operations/settings/{setting_key}
```

Supported settings control fresh stock-analysis pricing, daily report unlock pricing, rewarded-ad rewards and limits, community submission limits, and whether new notifications can be created. Every change records the previous and new value in the administrator audit trail.

## Operational dashboard

```text
GET  /api/v1/admin/operations/overview
GET  /api/v1/admin/operations/users
GET  /api/v1/admin/operations/audit
GET  /api/v1/admin/operations/providers
POST /api/v1/admin/operations/providers/probe
```

The overview returns user, moderation, prediction-verification, wallet, and notification metrics. Provider probes record bounded market-data and AI checks with status, latency, observation time, and safe diagnostics.

The Flutter dashboard also reuses the protected community administration APIs for pending discussion moderation and account block/unblock actions.

## Notifications

```text
POST /api/v1/notifications/devices
POST /api/v1/notifications/devices/unregister
GET  /api/v1/notifications
POST /api/v1/notifications/read-all
POST /api/v1/notifications/{notification_id}/read

POST /api/v1/admin/operations/notifications/broadcast
```

Notifications are persisted before Push delivery. Device tokens are represented by a SHA-256 lookup hash and an encrypted token value. Delivery attempts are recorded independently for each device.

`FCM_DELIVERY_MODE` supports:

- `disabled`: persist in-app notifications and skip Push;
- `stub`: deterministic test delivery without contacting Firebase;
- `live`: Firebase Cloud Messaging HTTP v1.

Live mode additionally requires `FCM_PROJECT_ID` and `FCM_SERVICE_ACCOUNT_JSON`. The service-account value may contain JSON directly or point to a mounted JSON file. These credentials must remain server-side and must never be included in Flutter assets or source control.

Flutter initializes Firebase defensively. Until valid Android/iOS Firebase project files are provided, the in-app notification inbox continues to work and Push registration is skipped without breaking authentication or navigation.

## Current live Push status

As of 2026-07-26, no live FCM Push notification has been configured or sent for this project. The in-app inbox and `disabled`/`stub` delivery paths are implemented, but `live` mode is deliberately deferred and is not production-verified yet.

Live Push will be completed later as a separate pre-release task after the Firebase project, platform configuration files, deployment secrets, and a physical test device are available.

## Validation and release gates

Backend imports are normalized according to the repository CI generation: external dependencies remain separate, while `app` and `sahmi_kasban` imports share the internal package group.

Before enabling live Push in production:

1. configure the Firebase project and platform application files;
2. configure the service-account credential as a deployment secret;
3. run a real device-token registration;
4. send a test broadcast to selected accounts;
5. confirm the in-app notification, Push delivery, read state, and delivery audit records;
6. verify that non-administrator accounts receive HTTP 403 from every administration endpoint.