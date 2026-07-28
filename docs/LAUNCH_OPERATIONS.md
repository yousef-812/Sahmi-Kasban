# Launch Operations — Fly, Neon, and Sentry

This runbook is the release gate for Sahmi Kasban staging and the first public release.

## 1. Sentry activation

Backend support is already integrated. Add the Backend DSN as a Fly secret:

```powershell
flyctl secrets set SENTRY_DSN="https://PUBLIC_KEY@SENTRY_HOST/PROJECT_ID" -a sahmi-kasban
```

Non-secret Fly defaults are committed:

- `SENTRY_RELEASE=sahmi-kasban-backend@0.7.0`
- `SENTRY_TRACES_SAMPLE_RATE=0.10`
- no default PII is sent;
- request IDs are attached to errors and logs.

For the Android release, pass the Flutter DSN and release at build time:

```text
--dart-define=SENTRY_DSN=<flutter project DSN>
--dart-define=SENTRY_ENVIRONMENT=production
--dart-define=SENTRY_RELEASE=sahmi-kasban-mobile@0.7.0+13
--dart-define=SENTRY_TRACES_SAMPLE_RATE=0.10
```

After deployment, sign in with an administrator account and call:

```text
POST /api/v1/admin/operations/quality/sentry-test
```

Acceptance:

1. The API returns `status=sent`.
2. The marker appears in the correct Sentry project and environment.
3. A team alert is configured for new fatal errors, error-rate growth, and p95 latency regressions.
4. No email, token, request body, or credential appears in the event.

## 2. External Fly acceptance

A manual GitHub Actions workflow named **Fly Staging Acceptance** runs from GitHub-hosted infrastructure, not from the application container. It checks:

- process health;
- Neon database reachability;
- every public legal/deletion page;
- 200 concurrent health requests with 25 workers;
- zero failed requests;
- p95 at or below 1,000 ms.

It can also run locally:

```powershell
python scripts/staging_acceptance.py --base-url https://sahmi-kasban.fly.dev
```

Run it after every staging deployment and before promoting a build to Google Play testing.

## 3. Neon backup and restore

Use Neon **Backup & Restore** before a migration or production release:

1. Open the Neon project used by `sahmi-kasban`.
2. Open **Backup & Restore**.
3. Create a named snapshot such as `before-release-0.7.0` when snapshots are available on the plan.
4. Confirm the project's history-retention window is enabled and long enough for the release observation period.
5. Record the snapshot/time and deployed Git commit in the release log.

For a portable secondary backup, run `pg_dump` from a trusted machine using the direct migration connection string:

```powershell
pg_dump --dbname "$env:MIGRATION_DATABASE_URL" --format=custom --compress=9 --no-owner --no-acl --file "sahmi-kasban-$(Get-Date -Format yyyyMMdd-HHmmss).dump"
pg_restore --list .\sahmi-kasban-*.dump | Out-Null
```

Store dumps only in encrypted storage. Never upload a database dump to GitHub artifacts or commit it to the repository.

### Restore drill

Before the public release, perform one drill on a separate Neon branch:

1. Create a branch from the production/staging branch at the chosen point in time.
2. connect the Backend locally or in an isolated environment;
3. run `/api/v1/health/database`;
4. verify users, wallets, analysis access, reports, and migrations;
5. delete the drill branch when finished.

## 4. Fly rollback

Before each deploy, record the current release image:

```powershell
flyctl releases -a sahmi-kasban --image
```

Rollback with the committed helper:

```powershell
.\scripts\fly_rollback.ps1 -Image "registry.fly.io/sahmi-kasban@sha256:..."
```

The helper redeploys the selected image and verifies both application and database health. A rollback is not considered complete until logs and health checks are stable.

## 5. Release observation

For the first 24 hours:

- check Fly logs and `/api/v1/admin/operations/quality` at least every two hours;
- inspect Sentry for crashes and slow traces;
- check the 17:00 Cairo daily report job;
- check Monday weekly grants;
- verify Groq moderation retries;
- watch Neon connection, storage, and compute usage;
- pause rollout if error rate exceeds 5% or p95 exceeds 1,000 ms with a meaningful sample.

## 6. Secret hygiene

- Keep `SECRET_KEY`, database URLs, SMTP password, Groq keys, Sentry DSNs, Firebase service-account JSON, Google Play service-account JSON, and billing encryption keys in platform secrets only.
- Rotate any secret that appeared in source history, screenshots, logs, or chat.
- Do not expose server credentials through Flutter dart-defines; only public Sentry DSNs and public mobile configuration belong in the application build.
