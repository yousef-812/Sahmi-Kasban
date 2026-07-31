from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlparse

from cryptography.fernet import Fernet

from app.core.config import Environment, Settings, get_settings

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_REQUIRED_SERVICE_ACCOUNT_FIELDS = frozenset(
    {"project_id", "client_email", "private_key"}
)


class ProductionReadinessError(RuntimeError):
    """Raised when a production process starts with unsafe configuration."""


def _service_account_payload(
    raw: str,
    *,
    label: str,
    allow_path: bool = True,
) -> tuple[dict[str, object] | None, str | None]:
    value = raw.strip()
    if not value:
        return None, f"{label} is required"
    try:
        if allow_path and not value.startswith("{"):
            path = Path(value)
            if not path.is_file():
                return None, f"{label} must reference a readable JSON file"
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            payload = json.loads(value)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        source = (
            "valid service-account JSON or a readable JSON path"
            if allow_path
            else "valid service-account JSON"
        )
        return None, f"{label} must contain {source}"
    if not isinstance(payload, dict):
        return None, f"{label} must decode to a JSON object"
    missing = sorted(_REQUIRED_SERVICE_ACCOUNT_FIELDS.difference(payload))
    if missing:
        return None, f"{label} is missing required service-account fields"
    return payload, None


def production_readiness_issues(
    settings: Settings,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, ...]:
    """Return safe, non-secret production configuration failures."""

    if settings.app_env is not Environment.PRODUCTION:
        return ()

    env = os.environ if environ is None else environ
    issues: list[str] = []

    if settings.debug:
        issues.append("DEBUG must be false in production")

    public_url = urlparse(settings.app_public_url.strip())
    if public_url.scheme != "https" or not public_url.netloc:
        issues.append("APP_PUBLIC_URL must be an absolute https:// URL in production")

    for origin in settings.cors_origin_list:
        parsed = urlparse(origin)
        if origin == "*" or parsed.scheme != "https" or not parsed.netloc:
            issues.append("CORS_ORIGINS may contain only explicit https:// origins in production")
            break

    admin_emails = tuple(
        item.strip().casefold()
        for item in env.get("ADMIN_EMAILS", "").split(",")
        if item.strip()
    )
    if not admin_emails:
        issues.append("ADMIN_EMAILS must contain at least one production administrator")
    elif any(_EMAIL_PATTERN.fullmatch(email) is None for email in admin_emails):
        issues.append("ADMIN_EMAILS contains an invalid email address")

    if env.get("FCM_DELIVERY_MODE", "disabled").strip().lower() != "live":
        issues.append("FCM_DELIVERY_MODE must be live in production")
    fcm_project_id = env.get("FCM_PROJECT_ID", "").strip()
    if not fcm_project_id:
        issues.append("FCM_PROJECT_ID is required in production")

    fcm_raw = env.get("FCM_SERVICE_ACCOUNT_JSON", "").strip()
    adc_path = env.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    fcm_payload: dict[str, object] | None = None
    if fcm_raw:
        fcm_payload, fcm_issue = _service_account_payload(
            fcm_raw,
            label="FCM_SERVICE_ACCOUNT_JSON",
        )
        if fcm_issue:
            issues.append(fcm_issue)
    elif adc_path:
        fcm_payload, fcm_issue = _service_account_payload(
            adc_path,
            label="GOOGLE_APPLICATION_CREDENTIALS",
        )
        if fcm_issue:
            issues.append(fcm_issue)
    else:
        issues.append(
            "FCM_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS is required in production"
        )
    if fcm_payload and fcm_project_id:
        credential_project = str(fcm_payload.get("project_id") or "").strip()
        if credential_project != fcm_project_id:
            issues.append("FCM_PROJECT_ID must match the Firebase service-account project_id")

    _, play_issue = _service_account_payload(
        settings.google_play_service_account_json,
        label="GOOGLE_PLAY_SERVICE_ACCOUNT_JSON",
        allow_path=False,
    )
    if play_issue:
        issues.append(play_issue)

    billing_key = settings.billing_token_encryption_key.strip()
    try:
        Fernet(billing_key.encode("ascii"))
    except (UnicodeEncodeError, ValueError):
        issues.append("BILLING_TOKEN_ENCRYPTION_KEY must be a valid Fernet key")

    if settings.sentry_dsn.strip() and not settings.sentry_release.strip():
        issues.append("SENTRY_RELEASE is required when SENTRY_DSN is configured")

    sender = settings.smtp_from_email.strip().casefold()
    if _EMAIL_PATTERN.fullmatch(sender) is None or sender.endswith(".local"):
        issues.append("SMTP_FROM_EMAIL must be a deliverable non-local email address")

    return tuple(dict.fromkeys(issues))


def enforce_production_readiness(
    settings: Settings,
    environ: Mapping[str, str] | None = None,
) -> None:
    issues = production_readiness_issues(settings, environ)
    if issues:
        details = "\n".join(f"- {issue}" for issue in issues)
        raise ProductionReadinessError(
            "Production readiness checks failed:\n" + details
        )


def main() -> None:
    settings = get_settings()
    enforce_production_readiness(settings)
    print(f"Production readiness checks passed for {settings.app_name}.")


if __name__ == "__main__":
    main()
