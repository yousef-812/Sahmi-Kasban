from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from functools import lru_cache

from app.core.config import Environment, Settings, get_settings

logger = logging.getLogger(__name__)


class AccountEmailService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def send_email_verification(self, email: str, token: str) -> None:
        verification_url = (
            f"{self.settings.app_public_url.rstrip('/')}/verify-email?token={token}"
        )
        self._send(
            recipient=email,
            subject="تأكيد بريدك في سهمي كسبان",
            body=(
                "مرحبًا بك في سهمي كسبان.\n\n"
                "استخدم الرابط التالي لتأكيد بريدك الإلكتروني:\n"
                f"{verification_url}\n\n"
                "ينتهي الرابط تلقائيًا بعد المدة المحددة."
            ),
        )

    def send_password_reset(self, email: str, token: str) -> None:
        reset_url = f"{self.settings.app_public_url.rstrip('/')}/reset-password?token={token}"
        self._send(
            recipient=email,
            subject="إعادة تعيين كلمة مرور سهمي كسبان",
            body=(
                "وصلنا طلب لإعادة تعيين كلمة المرور.\n\n"
                "استخدم الرابط التالي لإكمال العملية:\n"
                f"{reset_url}\n\n"
                "تجاهل الرسالة إذا لم تطلب تغيير كلمة المرور."
            ),
        )

    def _send(self, *, recipient: str, subject: str, body: str) -> None:
        if not self.settings.smtp_host:
            if self.settings.app_env in {Environment.DEVELOPMENT, Environment.TEST}:
                logger.warning(
                    "SMTP is not configured; account email for %s was not delivered. Body: %s",
                    recipient,
                    body,
                )
                return
            raise RuntimeError("SMTP is not configured")

        message = EmailMessage()
        message["From"] = self.settings.smtp_from_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            if self.settings.smtp_username:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)


@lru_cache
def get_account_email_service() -> AccountEmailService:
    return AccountEmailService()
