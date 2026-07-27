from __future__ import annotations

import html
import logging
import smtplib
from email.message import EmailMessage
from functools import lru_cache

from app.core.config import Environment, Settings, get_settings

logger = logging.getLogger(__name__)


class AccountEmailService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def send_email_verification(self, email: str, code: str) -> None:
        safe_code = html.escape(code)
        self._send(
            recipient=email,
            subject="رمز تأكيد بريدك في سهمي كسبان",
            body=(
                "مرحبًا بك في سهمي كسبان.\n\n"
                f"رمز تأكيد بريدك الإلكتروني هو: {code}\n\n"
                "الرمز صالح لمدة 10 دقائق. لا تشاركه مع أي شخص.\n"
                "تجاهل الرسالة إذا لم تطلب إنشاء الحساب."
            ),
            html_body=self._verification_html(safe_code),
        )

    def send_password_reset(self, email: str, token: str) -> None:
        reset_url = f"{self.settings.app_public_url.rstrip('/')}/reset-password?token={token}"
        safe_url = html.escape(reset_url, quote=True)
        self._send(
            recipient=email,
            subject="إعادة تعيين كلمة مرور سهمي كسبان",
            body=(
                "وصلنا طلب لإعادة تعيين كلمة المرور.\n\n"
                "استخدم الرابط التالي لإكمال العملية:\n"
                f"{reset_url}\n\n"
                "تجاهل الرسالة إذا لم تطلب تغيير كلمة المرور."
            ),
            html_body=self._action_html(
                title="إعادة تعيين كلمة المرور",
                message="وصلنا طلب لتغيير كلمة مرور حسابك.",
                button_label="إعادة تعيين كلمة المرور",
                button_url=safe_url,
                footnote="ينتهي رابط الاستعادة تلقائيًا بعد المدة المحددة.",
            ),
        )

    def _send(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> None:
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
        if html_body:
            message.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            if self.settings.smtp_username:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)

    def _verification_html(self, code: str) -> str:
        return f"""\
<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>تأكيد البريد الإلكتروني</title>
  </head>
  <body style="margin:0;background:#f4f7f5;font-family:Tahoma,Arial,sans-serif;color:#18332a;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f7f5;padding:28px 12px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border-radius:24px;overflow:hidden;box-shadow:0 12px 40px rgba(20,76,57,.10);">
          <tr>
            <td style="background:#176f54;padding:30px 34px;text-align:center;color:#ffffff;">
              <div style="font-size:27px;font-weight:800;letter-spacing:.2px;">سهمي كسبان</div>
              <div style="margin-top:7px;font-size:14px;opacity:.88;">تحليلك أوضح وقراراتك أهدأ</div>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 34px;text-align:right;">
              <h1 style="margin:0 0 14px;font-size:24px;line-height:1.5;color:#173c30;">أكد بريدك الإلكتروني</h1>
              <p style="margin:0;color:#52675f;font-size:16px;line-height:1.9;">مرحبًا بك. أدخل الرمز التالي داخل التطبيق لإكمال إنشاء حسابك:</p>
              <div style="margin:28px 0;padding:22px;border:1px solid #cce2d9;border-radius:18px;background:#edf7f2;text-align:center;">
                <div style="font-size:13px;color:#5c746a;margin-bottom:9px;">رمز التأكيد</div>
                <div dir="ltr" style="font-family:Arial,sans-serif;font-size:38px;font-weight:800;letter-spacing:11px;color:#176f54;">{code}</div>
              </div>
              <p style="margin:0 0 10px;color:#52675f;font-size:15px;line-height:1.8;">الرمز صالح لمدة <strong style="color:#173c30;">10 دقائق</strong>.</p>
              <p style="margin:0;color:#7a8b84;font-size:13px;line-height:1.8;">لا تشارك الرمز مع أي شخص. تجاهل الرسالة إذا لم تطلب إنشاء هذا الحساب.</p>
            </td>
          </tr>
          <tr>
            <td style="padding:20px 34px;background:#f7faf8;text-align:center;color:#829089;font-size:12px;line-height:1.7;">رسالة آلية من سهمي كسبان — لا يلزم الرد عليها.</td>
          </tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>
"""

    def _action_html(
        self,
        *,
        title: str,
        message: str,
        button_label: str,
        button_url: str,
        footnote: str,
    ) -> str:
        return f"""\
<!doctype html>
<html lang="ar" dir="rtl">
  <body style="margin:0;background:#f4f7f5;font-family:Tahoma,Arial,sans-serif;color:#18332a;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:28px 12px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#fff;border-radius:24px;overflow:hidden;box-shadow:0 12px 40px rgba(20,76,57,.10);">
          <tr><td style="background:#176f54;padding:30px;text-align:center;color:#fff;font-size:27px;font-weight:800;">سهمي كسبان</td></tr>
          <tr><td style="padding:36px 34px;">
            <h1 style="margin:0 0 14px;font-size:24px;color:#173c30;">{html.escape(title)}</h1>
            <p style="margin:0 0 26px;color:#52675f;font-size:16px;line-height:1.9;">{html.escape(message)}</p>
            <div style="text-align:center;margin:28px 0;">
              <a href="{button_url}" style="display:inline-block;background:#176f54;color:#fff;text-decoration:none;padding:14px 28px;border-radius:12px;font-weight:700;">{html.escape(button_label)}</a>
            </div>
            <p style="margin:0;color:#7a8b84;font-size:13px;line-height:1.8;">{html.escape(footnote)}</p>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>
"""


@lru_cache
def get_account_email_service() -> AccountEmailService:
    return AccountEmailService()
