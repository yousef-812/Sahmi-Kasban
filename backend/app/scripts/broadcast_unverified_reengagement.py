from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

# Add backend directory to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.entities import User
from app.services.email import AccountEmailService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("reengagement_broadcast")

SUBJECT = "استكمل تفعيل حسابك واستفد من الدخول السريع عبر جوجل في سهمي كسبان"

PLAIN_BODY_TEMPLATE = """مرحباً بك في سهمي كسبان.

لاحظنا أنك بدأت تسجيل حسابك معنا ولم تكتمل خطوة التفعيل بعد.

يسعدنا إبلاغك بتوفير ميزة الدخول السريع بنقرة واحدة باستخدام حساب جوجل (Google Sign-In) دون الحاجة لانتظار أكواد التفعيل.

ماذا يقدم لك تطبيق سهمي كسبان؟
- تحليلات وتقارير يومية لأهم أسهم البورصة المصرية (EGX).
- توقعات مدعومة بالذكاء الاصطناعي لحركة الأسهم.
- محفظة افتراضية وعملات مجانية ترحيبية فور تسجيلك.
- إشعارات لحظية بأحدث الفرص والتحديثات.

افتح التطبيق وسجل دخولك الآن عبر جوجل للاستفادة من كافة الخدمات.

فريق سهمي كسبان
https://sahmi-kasban.bdaey.com
"""

HTML_BODY_TEMPLATE = """<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سهمي كسبان</title>
  </head>
  <body style="margin: 0; padding: 0; background-color: #0b1329; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #e2e8f0; direction: rtl; text-align: right;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0b1329; padding: 20px 10px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" style="max-width: 600px; background-color: #111c38; border-radius: 12px; border: 1px solid #1e2d54; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <!-- Header -->
            <tr>
              <td align="center" style="padding-bottom: 25px; border-bottom: 1px solid #1e2d54;">
                <h1 style="margin: 0; font-size: 26px; color: #38bdf8; font-weight: 700;">سهمي كسبان</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px; color: #94a3b8;">منصتك الذكية لتحليل وتوقعات البورصة المصرية</p>
              </td>
            </tr>
            <!-- Content -->
            <tr>
              <td style="padding: 25px 0;">
                <h2 style="margin: 0 0 15px 0; font-size: 20px; color: #f8fafc;">أهلاً بك،</h2>
                <p style="font-size: 15px; line-height: 1.7; color: #cbd5e1; margin-bottom: 20px;">
                  لاحظنا أنك بدأت رحلتك معنا في تطبيق <strong>سهمي كسبان</strong> ولم تكتمل خطوة تفعيل حسابك بعد.
                </p>
                <div style="background-color: #1e293b; border-right: 4px solid #38bdf8; padding: 15px 20px; border-radius: 6px; margin-bottom: 25px;">
                  <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #38bdf8; font-weight: 600;">
                    ميزة جديدة: تسجيل الدخول السريع عبر Google
                  </p>
                  <p style="margin: 5px 0 0 0; font-size: 14px; color: #94a3b8;">
                    يمكنك الآن الدخول بنقرة واحدة باستخدام حساب جوجل الخاص بك دون الحاجة لانتظار أكواد التفعيل.
                  </p>
                </div>
                <h3 style="font-size: 16px; color: #f1f5f9; margin-bottom: 12px;">مميزات تنتظرك داخل التطبيق:</h3>
                <ul style="padding-right: 20px; margin: 0 0 25px 0; font-size: 14px; line-height: 1.8; color: #cbd5e1;">
                  <li style="margin-bottom: 8px;"><strong>تحليلات وتقارير يومية:</strong> متابعة دقيقة لأهم أسهم البورصة المصرية (EGX).</li>
                  <li style="margin-bottom: 8px;"><strong>توقعات الذكاء الاصطناعي:</strong> قراءة متقدمة لحركة الأسهم وتحديد الاتجاهات.</li>
                  <li style="margin-bottom: 8px;"><strong>محفظة افتراضية وعملات ترحيبية:</strong> ابدأ تجربتك فوراً مع رصيد عملات مجاني.</li>
                  <li style="margin-bottom: 8px;"><strong>إشعارات لحظية:</strong> ليصلك كل جديد وتحديث في الوقت المناسب.</li>
                </ul>
                <div style="text-align: center; margin: 30px 0 15px 0;">
                  <a href="https://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile" style="display: inline-block; background-color: #0284c7; color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 8px; font-weight: bold; font-size: 16px;">افتح التطبيق وسجل دخولك الآن</a>
                </div>
              </td>
            </tr>
            <!-- Footer -->
            <tr>
              <td align="center" style="padding-top: 20px; border-top: 1px solid #1e2d54; color: #64748b; font-size: 13px; line-height: 1.5;">
                <p style="margin: 0 0 5px 0;">فريق عمل سهمي كسبان</p>
                <p style="margin: 0;"><a href="https://sahmi-kasban.bdaey.com" style="color: #38bdf8; text-decoration: none;">sahmi-kasban.bdaey.com</a></p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

INVALID_DOMAIN_PATTERNS = [
    r"@example\.com$",
    r"@gmai\.com$",
    r"@gmaul\.com$",
    r"@gamil\.com$",
    r"\.coma$",
]


def is_valid_email(email: str) -> bool:
    email_clean = email.strip().casefold()
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email_clean):
        return False
    for pat in INVALID_DOMAIN_PATTERNS:
        if re.search(pat, email_clean):
            return False
    if email_clean == "xjdjjxgkhhjs@gmail.com":
        return False
    return True


def load_sent_emails(log_file: Path) -> set[str]:
    if log_file.exists():
        try:
            data = json.loads(log_file.read_text(encoding="utf-8"))
            return set(data.get("sent_emails", []))
        except Exception:
            pass
    return set()


def save_sent_email(log_file: Path, email: str) -> None:
    sent = load_sent_emails(log_file)
    sent.add(email.strip().casefold())
    log_file.write_text(
        json.dumps({"sent_emails": sorted(list(sent))}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_broadcast(*, interval_seconds: int = 600, dry_run: bool = False) -> None:
    log_file = Path("/tmp/reengagement_sent_emails.json")
    if not log_file.parent.exists():
        log_file = Path("reengagement_sent_emails.json")

    sent_emails = load_sent_emails(log_file)

    db = SessionLocal()
    try:
        user_emails = (
            db.query(User.email)
            .filter(User.email_verified == False)
            .order_by(User.created_at.desc())
            .all()
        )
        target_emails = [
            email.strip()
            for (email,) in user_emails
            if is_valid_email(email)
            and email.strip().casefold() not in sent_emails
        ]

        logger.info(
            "Found %d valid unverified target emails (%d already sent out of %d total unverified)",
            len(target_emails),
            len(sent_emails),
            len(user_emails),
        )

        if dry_run:
            logger.info("[DRY RUN MODE] Target email queue:")
            for idx, mail in enumerate(target_emails, 1):
                logger.info("  %d. %s", idx, mail)
            return

        email_service = AccountEmailService()

        for idx, recipient in enumerate(target_emails, 1):
            logger.info(
                "[%d/%d] Sending re-engagement email to %s...",
                idx,
                len(target_emails),
                recipient,
            )
            try:
                email_service._send(
                    recipient=recipient,
                    subject=SUBJECT,
                    body=PLAIN_BODY_TEMPLATE,
                    html_body=HTML_BODY_TEMPLATE,
                )
                save_sent_email(log_file, recipient)
                logger.info(
                    "[%d/%d] Successfully sent to %s.",
                    idx,
                    len(target_emails),
                    recipient,
                )
            except Exception as exc:
                logger.error(
                    "[%d/%d] Failed to send email to %s: %s",
                    idx,
                    len(target_emails),
                    recipient,
                    exc,
                )

            if idx < len(target_emails):
                logger.info(
                    "Waiting %d seconds (10 mins) before next email...",
                    interval_seconds,
                )
                time.sleep(interval_seconds)

        logger.info("Broadcast completed cleanly for all target emails.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Broadcast re-engagement email to unverified users every 10 minutes"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=600,
        help="Interval in seconds between emails (default: 600 = 10 mins)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run without sending actual emails",
    )
    args = parser.parse_args()
    run_broadcast(interval_seconds=args.interval, dry_run=args.dry_run)
