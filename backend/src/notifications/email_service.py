import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.configs.app import settings


async def send_email(to_email: str, subject: str, body: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_sync, to_email, subject, body)


def _send_sync(to_email: str, subject: str, body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.email.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(settings.email.smtp_host, settings.email.smtp_port) as smtp:
        if settings.email.smtp_tls:
            smtp.starttls()
        if settings.email.smtp_user and settings.email.smtp_password:
            smtp.login(settings.email.smtp_user, settings.email.smtp_password)
        smtp.sendmail(settings.email.smtp_from, [to_email], msg.as_string())
