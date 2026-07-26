from __future__ import annotations

import re
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2]
FORBIDDEN_FILENAMES = {
    ".env",
    "google-services.json",
    "GoogleService-Info.plist",
    "service-account.json",
    "service_account.json",
}
SKIP_PARTS = {".git", ".dart_tool", ".github/.cache", "build", "__pycache__"}
TEXT_SUFFIXES = {
    ".dart",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Google service-account private key": re.compile(
        r'"private_key"\s*:\s*"-----BEGIN PRIVATE KEY-----'
    ),
    "GitHub token": re.compile(r"\bgh[oprsu]_[A-Za-z0-9]{30,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
}


def should_skip(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    joined = "/".join(relative.parts)
    return path.resolve() == SCRIPT_PATH or any(
        marker in relative.parts or marker in joined for marker in SKIP_PARTS
    )


def main() -> None:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        if path.name in FORBIDDEN_FILENAMES:
            failures.append(f"forbidden tracked configuration file: {path.relative_to(ROOT)}")
            continue
        if path.suffix not in TEXT_SUFFIXES or path.stat().st_size > 1_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                failures.append(f"{label} detected in {path.relative_to(ROOT)}")

    if failures:
        details = "\n".join(f"- {failure}" for failure in failures)
        raise SystemExit(f"Security gate failed:\n{details}")
    print("Security gate passed: no committed secrets or forbidden provider files found.")


if __name__ == "__main__":
    main()
