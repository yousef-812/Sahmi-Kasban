# Fly.io staging deployment

This deployment path runs Sahmi Kasban on Fly.io while keeping Neon PostgreSQL in Frankfurt and Firebase registered for the Android application.

## Architecture

- Flutter Android application with Firebase configuration injected during CI.
- FastAPI backend on Fly.io in `fra`.
- Neon PostgreSQL in Frankfurt.
- Pooled Neon connection for normal API traffic.
- Direct Neon connection for Alembic release migrations.
- Firebase Cloud Messaging delivery remains disabled until a server credential that can run outside Google Cloud is available.

## App configuration

The repository root contains `fly.toml` with:

- app name `sahmi-kasban`;
- Docker build from `backend/Dockerfile` with the repository root as build context;
- internal port `8080`;
- Frankfurt as the primary region;
- one shared CPU and 512 MB memory;
- automatic stop/start with zero always-running Machines;
- readiness checks against `/api/v1/health/ready`;
- `python -m alembic upgrade head` as the release command.

The release command inherits Fly secrets and stops the deployment if a migration fails.

## Required Fly secrets

Do not put these values in the dashboard's ordinary Environment Variables fields:

- `DATABASE_URL`: pooled Neon URL, using the `postgresql+psycopg://` scheme.
- `MIGRATION_DATABASE_URL`: direct Neon URL, using the `postgresql+psycopg://` scheme.
- `SECRET_KEY`: stable random application secret with at least 32 characters.

### Safe Windows setup

Create a temporary file named `fly-secrets.env` outside source control:

```text
DATABASE_URL=<POOLED_NEON_URL>
MIGRATION_DATABASE_URL=<DIRECT_NEON_URL>
SECRET_KEY=<LONG_RANDOM_SECRET>
```

Create the Fly app without deploying it:

```powershell
fly apps create sahmi-kasban --org BDAEY
```

If the app already exists, skip that command.

Import the temporary file into Fly's encrypted secrets vault:

```powershell
cmd /c "fly secrets import -a sahmi-kasban < fly-secrets.env"
```

Delete the local temporary file immediately:

```powershell
Remove-Item fly-secrets.env
```

Confirm that Fly lists only secret names and digests:

```powershell
fly secrets list -a sahmi-kasban
```

## Deploy

Run from the repository root after this change is merged:

```powershell
fly deploy -a sahmi-kasban
```

The expected sequence is:

1. build the root repository using `backend/Dockerfile`;
2. start a temporary release Machine;
3. connect to Neon through `MIGRATION_DATABASE_URL`;
4. run Alembic to `head`;
5. create or update the application Machine;
6. pass the readiness check;
7. expose the API through HTTPS.

## Dashboard values

For a GitHub-connected dashboard deployment after secrets already exist:

- App name: `sahmi-kasban`
- Organization: `BDAEY`
- Branch: `main`
- Region: `fra - Frankfurt`
- Internal port: `8080`
- CPU: `shared-cpu-1x`
- Memory: `512MB`
- Managed Postgres: disabled
- Working directory: `./`
- Config path: `./fly.toml`
- Ordinary Environment Variables: leave blank; non-sensitive values are already in `fly.toml`

## Validation after deployment

```powershell
fly status -a sahmi-kasban
fly checks list -a sahmi-kasban
fly logs -a sahmi-kasban
```

Then verify:

- `https://sahmi-kasban.fly.dev/api/v1/health`
- `https://sahmi-kasban.fly.dev/api/v1/health/ready`

The second endpoint must report the database check as ready.

## Firebase status

The Android app is registered and can obtain an FCM device token. The backend records device tokens and in-app notifications. External push delivery is intentionally set to `disabled` on Fly until an approved service-account credential or another supported workload identity path is available. No Google private key is committed to the repository.
