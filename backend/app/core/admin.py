from __future__ import annotations

import os


def configured_admin_emails() -> frozenset[str]:
    return frozenset(
        item.strip().casefold() for item in os.getenv("ADMIN_EMAILS", "").split(",") if item.strip()
    )


def is_admin_email(email: str) -> bool:
    return email.strip().casefold() in configured_admin_emails()
