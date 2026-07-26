# Phase 9 Quality Gates

This document defines the production quality controls completed in PR #20. The controls are intentionally useful before any external monitoring account is connected, while supporting Sentry when deployment secrets are supplied.

## 1. Request observability

Every Backend response includes:

- `X-Request-ID`: a validated caller-provided identifier or a generated UUID;
- `X-Response-Time-Ms`: server processing duration in milliseconds.

The Backend emits structured JSON logs by default. Request bodies, authorization headers, cookies, passwords, tokens, purchase tokens, and provider credentials are never logged by the request middleware.

Rolling process-local metrics track:

- request count and in-flight requests;
- HTTP status counts;
- server-error count and error rate;
- average, P95, and maximum latency;
- requests that exceed `REQUEST_SLOW_THRESHOLD_MS`.

The process-local window is for immediate diagnostics. Long-term retention, cross-instance aggregation, release comparison, and team notifications are provided by the configured external monitoring platform.

## 2. Sentry activation

### Backend

Configure deployment secrets and settings:

```text
SENTRY_DSN=<backend project DSN>
SENTRY_RELEASE=sahmi-kasban-api@<release>
SENTRY_TRACES_SAMPLE_RATE=0.10
APP_ENV=staging|production
```

No DSN is committed. `send_default_pii` is disabled, and production/staging configuration validation requires a non-empty DSN.

### Flutter

Build with deployment-only Dart defines:

```bash
flutter build appbundle \
  --dart-define=API_BASE_URL=https://api.example.com/api/v1 \
  --dart-define=APP_ENV=production \
  --dart-define=SENTRY_DSN=<mobile project DSN> \
  --dart-define=SENTRY_RELEASE=sahmi-kasban-mobile@<release> \
  --dart-define=SENTRY_TRACES_SAMPLE_RATE=0.10
```

When the mobile DSN is absent, the application still starts, logs uncaught platform errors locally, and shows an Arabic accessible fallback widget for framework rendering failures.

## 3. Health and administration APIs

Public endpoints:

- `GET /api/v1/health` — liveness;
- `GET /api/v1/health/database` — direct database probe;
- `GET /api/v1/health/ready` — readiness response with explicit checks and HTTP 503 when a required dependency is unavailable.

Administrator endpoint:

- `GET /api/v1/admin/operations/quality`

The administrator quality response includes rolling request metrics, latest provider probes, stale-probe flags, configured thresholds, Sentry activation state, and normalized `healthy`, `degraded`, or `critical` status.

Default alerts:

- critical when server error rate reaches 5% after at least 20 requests;
- warning when request P95 reaches 1,000 ms after at least 20 requests;
- critical when a provider probe reports `failed`;
- warning when a provider probe is degraded or older than 60 minutes;
- critical when external error reporting is disabled in staging or production.

All thresholds are environment-configurable.

## 4. CI security gates

Repository lint now runs:

1. committed-secret and forbidden-provider-file scan;
2. Bandit high-severity/high-confidence scan for Backend application code;
3. Python compilation and Ruff checks.

Repository tests now run:

1. Python dependency vulnerability audit;
2. core and Backend tests;
3. a 200-request/25-concurrency in-process load smoke;
4. full Alembic upgrade, downgrade, and rebuild;
5. existing optional TradingView live smoke when explicitly enabled.

Flutter CI continues to require formatting, static analysis, all tests, and Android debug APK creation.

## 5. Load baseline

The deterministic CI smoke sends 200 concurrent liveness requests with a concurrency cap of 25. It requires:

- every response to return HTTP 200;
- every response to include a unique request ID;
- P95 server round-trip below 1,000 ms in the in-process CI environment.

This is a regression gate, not a production capacity claim. Before public launch, staging must also be tested through the real reverse proxy, database pool, network, and production-like worker count.

Recommended staging scenarios:

- report unlock concurrency with repeated idempotency keys;
- wallet and rewarded-ad callbacks under retries;
- simultaneous report evaluation/backfill requests;
- discussion creation/reporting rate limits;
- administration authorization and object-access attempts;
- market-data and AI provider timeout/degradation behavior.

## 6. UX and accessibility acceptance

PR #20 adds an Arabic, RTL, live-region fallback for framework rendering errors and tests its semantic label. Release acceptance still requires device testing for:

- Android small and large screens;
- system text scaling up to at least 200%;
- TalkBack navigation and meaningful control labels;
- loading, empty, offline, timeout, and retry states;
- repeated taps on financial actions;
- long Arabic strings and large result sets;
- confirmation copy for purchases, wallet changes, and administrative corrections.

## 7. Release boundaries

The following remain real-environment acceptance tasks rather than repository-only tests:

- creating Backend and Flutter Sentry projects and alert rules;
- configuring DSNs and release names in deployment secrets;
- verifying a captured staging exception and trace from both applications;
- routing critical Sentry alerts to the responsible team;
- performing production-like staging load tests;
- completing live Firebase Push, Google Play purchase, and AdMob SSV checks already documented in earlier phases.
