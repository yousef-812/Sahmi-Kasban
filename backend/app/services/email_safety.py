from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Pattern for basic email structure verification
_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# Known disposable, temporary, and test email domains that cause hard bounces
DISPOSABLE_DOMAINS: set[str] = {
    "example.com",
    "example.org",
    "example.net",
    "test.com",
    "test.org",
    "test.net",
    "invalid.com",
    "localhost",
    "local",
    "tempmail.com",
    "temp-mail.org",
    "10minutemail.com",
    "guerrillamail.com",
    "yopmail.com",
    "mailinator.com",
    "trashmail.com",
    "dispostable.com",
    "getnada.com",
    "sharklasers.com",
    "fakeinbox.com",
    "throwawaymail.com",
    "maildrop.cc",
    "crazymailing.com",
    "emailondeck.com",
    "mohmal.com",
    "mailnesia.com",
    "byom.de",
    "generator.email",
    "inboxalias.com",
    "tempmailo.com",
    "temp-mail.io",
    "mytemp.email",
    "bmail.com",
    "disposable.com",
    "tempinbox.com",
    "mailcatch.com",
    "trashmail.net",
    "tempmail.net",
    "nada.ltd",
    "mailnull.com",
    "spamgourmet.com",
    "guerrillamail.net",
    "guerrillamail.org",
    "sharklasers.com",
    "pokemail.net",
    "grr.la",
    "guerrillamailblock.com",
}

# Common domain typos -> corrected domain suggestion
COMMON_DOMAIN_TYPOS: dict[str, str] = {
    "gmai.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "gmaik.com": "gmail.com",
    "gmal.com": "gmail.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "hotmai.com": "hotmail.com",
    "hotmial.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outlokk.com": "outlook.com",
    "iclod.com": "icloud.com",
    "icould.com": "icloud.com",
}


class InvalidEmailError(ValueError):
    """Base exception for email validation failures."""


def validate_email_safety(email: str, check_dns: bool = True) -> str:
    """Validates email format, screens disposable domains, checks common typos,

    and performs DNS MX validation to prevent fake email hard bounces.
    Returns the normalized (lowercased, trimmed) email address.
    """
    normalized = email.strip().casefold()
    if not normalized:
        raise InvalidEmailError("يرجى إدخال البريد الإلكتروني.")

    if not _EMAIL_REGEX.match(normalized):
        raise InvalidEmailError("صيغة البريد الإلكتروني غير صحيحة.")

    parts = normalized.split("@")
    if len(parts) != 2:
        raise InvalidEmailError("صيغة البريد الإلكتروني غير صحيحة.")

    local_part, domain = parts[0], parts[1]

    if not local_part or len(local_part) > 64:
        raise InvalidEmailError("اسم اسم البريد الإلكتروني غير صالح.")

    if domain in DISPOSABLE_DOMAINS:
        logger.warning("Blocked registration/email request for disposable domain: %s", domain)
        raise InvalidEmailError("عفواً، لا يمكن استخدام نطاقات البريد المؤقتة أو الوهمية.")

    if domain in COMMON_DOMAIN_TYPOS:
        suggestion = COMMON_DOMAIN_TYPOS[domain]
        raise InvalidEmailError(f"هل تقصد @{suggestion}؟ يرجى تصحيح كتابة البريد الإلكتروني.")

    if check_dns:
        _verify_domain_mx(domain)

    return normalized


def _verify_domain_mx(domain: str) -> None:
    """Performs DNS MX record lookup to ensure the domain accepts emails."""
    try:
        import dns.resolver

        resolver = dns.resolver.Resolver()
        resolver.lifetime = 2.5
        resolver.timeout = 2.5

        answers = resolver.resolve(domain, "MX")
        exchanges = [r.exchange.to_text().strip(".").casefold() for r in answers]

        # Check for Null MX record (RFC 7505 - "." means domain does not accept email)
        if not exchanges or exchanges == [""] or exchanges == ["."]:
            logger.warning("Domain %s has Null MX record RFC 7505", domain)
            raise InvalidEmailError("نطاق البريد الإلكتروني غير قادر على استقبال الرسائل.")

    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
    ):
        logger.warning("Domain %s failed MX DNS resolution", domain)
        raise InvalidEmailError("نطاق البريد الإلكتروني غير موجود أو غير صالح.")
    except Exception as exc:
        # Fallback gracefully if DNS query fails due to timeout or network glitch
        logger.debug("DNS MX lookup skipped or timed out for %s: %s", domain, exc)
