"""Single source of truth for the latest published Android build.

Bump both values together with mobile/pubspec.yaml, and deploy only after the
build is available on Google Play for users.
"""

from __future__ import annotations

LATEST_APP_VERSION = "1.0.10+37"
LATEST_APP_VERSION_CODE = 37
