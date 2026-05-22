from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.email_service import send_email
from src.notifications.models import Notification
from src.notifications.repository import NotificationRepository

REMINDER_INTERVAL = timedelta(hours=1)


def determine_trigger(
    current_status: str,
    last: Notification | None,
    now: datetime,
) -> str | None:
    """
    Pure throttle logic. Returns the trigger type to send, or None if silent.

    Rules:
    - 'down'     — state just changed from up → down (or first ever check and it's down)
    - 'up'       — state just changed from down → up
    - 'reminder' — still down, but last notification was ≥ 1 hour ago
    """
    if current_status == "up":
        if last and last.trigger_type in ("down", "reminder"):
            return "up"
        return None

    # current_status == "down"
    if last is None or last.trigger_type == "up":
        return "down"

    # Was already down — check if reminder interval has passed
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
    """
    Returns (monitoring_task_id, url).
    incidents.monitoring_task_id → monitoring_tasks.id, monitoring_tasks.url
    """
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
    """
    Returns emails of all responsible persons for the given monitoring task.
    responsible_persons.monitoring_task_id → responsible_persons.email
    """
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


async def notify_incident(
    session: AsyncSession,
    incident_id: int,
    trigger_type: str,
) -> None:
    """
    Main entry point. Called when an incident is opened ('down') or resolved ('up').
    Fetches task URL + responsible emails from DB, applies throttling, sends emails.
    """
    incident = await _get_incident_data(session, incident_id)
    if incident is None:
        return
    monitoring_task_id, task_url = incident

    emails = await _get_responsible_emails(session, monitoring_task_id)
    if not emails:
        return

    repo = NotificationRepository(session)
    last = await repo.get_last_sent_for_monitoring_task(monitoring_task_id)
    now = datetime.now(UTC)

    trigger = determine_trigger(trigger_type, last, now)
    if trigger is None:
        return

    subject, body = _compose(task_url, trigger)

    for email in emails:
        record = await repo.create(
            {
                "monitoring_task_id": monitoring_task_id,
                "recipient_email": email,
                "trigger_type": trigger,
                "subject": subject,
                "body": body,
                "status": "pending",
            }
        )
        try:
            await send_email(email, subject, body)
            await repo.update(record, {"status": "sent", "sent_at": now})
        except Exception as exc:
            await repo.update(
                record, {"status": "failed", "error_message": str(exc)}
            )
