import asyncio
import smtplib
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.app import settings
from src.models.notification import Notification
from src.repositories.notification import NotificationRepository

REMINDER_INTERVAL = timedelta(hours=1)


def determine_trigger(
    current_status: str,
    last: Notification | None,
    now: datetime,
) -> str | None:
    if current_status == "up":
        if last and last.trigger_type in ("down", "reminder"):
            return "up"
        return None

    # current_status == "down"
    if last is None or last.trigger_type == "up":
        return "down"

    last_sent = last.sent_at
    if last_sent is not None:
        if last_sent.tzinfo is None:
            last_sent = last_sent.replace(tzinfo=UTC)
        if (now - last_sent) >= REMINDER_INTERVAL:
            return "reminder"

    return None


def _compose(endpoint_url: str, trigger_type: str) -> tuple[str, str]:
    if trigger_type == "down":
        subject = f"[ALERT] Сервис недоступен: {endpoint_url}"
        body = (
            f"Сервис {endpoint_url} не отвечает.\n"
            "Требуется немедленное внимание."
        )
    elif trigger_type == "up":
        subject = f"[RESOLVED] Сервис восстановлен: {endpoint_url}"
        body = f"Сервис {endpoint_url} снова доступен."
    else:  # reminder
        subject = f"[REMINDER] Сервис всё ещё недоступен: {endpoint_url}"
        body = (
            f"Сервис {endpoint_url} по-прежнему не отвечает.\n"
            "Пожалуйста, проверьте статус."
        )
    return subject, body


async def _get_incident_data(
    session: AsyncSession, incident_id: int
) -> tuple[int, str] | None:
    row = await session.execute(
        text(
            """
            SELECT mt.id, mt.url
            FROM incidents i
            JOIN monitoring_tasks mt ON mt.id = i.monitoring_task_id
            WHERE i.id = :incident_id
            """
        ),
        {"incident_id": incident_id},
    )
    result = row.first()
    if result is None:
        return None
    return result.id, result.url


async def _get_responsible_emails(
    session: AsyncSession, monitoring_task_id: int
) -> list[str]:
    rows = await session.execute(
        text(
            """
            SELECT rp.email
            FROM responsible_persons rp
            WHERE rp.monitoring_task_id = :monitoring_task_id
            """
        ),
        {"monitoring_task_id": monitoring_task_id},
    )
    return [row.email for row in rows]


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


async def _send_email(to_email: str, subject: str, body: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_sync, to_email, subject, body)


async def notify_incident(
    session: AsyncSession,
    incident_id: int,
    trigger_type: str,
) -> None:
    incident = await _get_incident_data(session, incident_id)
    if incident is None:
        return
    monitoring_task_id, task_url = incident

    emails = await _get_responsible_emails(session, monitoring_task_id)
    if not emails:
        return

    repo = NotificationRepository(session)
    last = await repo.get_last_sent_for_incident(incident_id)
    now = datetime.now(UTC)

    trigger = determine_trigger(trigger_type, last, now)
    if trigger is None:
        return

    subject, body = _compose(task_url, trigger)

    for email in emails:
        record = await repo.create(
            {
                "incident_id": incident_id,
                "recipient_email": email,
                "trigger_type": trigger,
                "subject": subject,
                "body": body,
                "status": "pending",
            }
        )
        try:
            await _send_email(email, subject, body)
            await repo.update(record, {"status": "sent", "sent_at": now})
        except Exception as exc:
            await repo.update(
                record, {"status": "failed", "error_message": str(exc)}
            )
