from datetime import datetime, timedelta, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.notification_service import (
    determine_trigger,
    _compose,
    _get_incident_data,
    _get_responsible_emails,
    notify_incident,
    _send_sync,
)


class TestDetermineTrigger:
    def test_determine_trigger_up_after_down(self):
        last = SimpleNamespace(
            trigger_type="down", sent_at=datetime.now(UTC) - timedelta(hours=2)
        )
        assert determine_trigger("up", last, datetime.now(UTC)) == "up"

    def test_determine_trigger_up_after_reminder(self):
        last = SimpleNamespace(
            trigger_type="reminder", sent_at=datetime.now(UTC) - timedelta(hours=2)
        )
        assert determine_trigger("up", last, datetime.now(UTC)) == "up"

    def test_determine_trigger_up_no_last(self):
        assert determine_trigger("up", None, datetime.now(UTC)) is None

    def test_determine_trigger_up_after_up(self):
        last = SimpleNamespace(
            trigger_type="up", sent_at=datetime.now(UTC) - timedelta(hours=2)
        )
        assert determine_trigger("up", last, datetime.now(UTC)) is None

    def test_determine_trigger_down_no_last(self):
        assert determine_trigger("down", None, datetime.now(UTC)) == "down"

    def test_determine_trigger_down_after_up(self):
        last = SimpleNamespace(
            trigger_type="up", sent_at=datetime.now(UTC) - timedelta(hours=2)
        )
        assert determine_trigger("down", last, datetime.now(UTC)) == "down"

    def test_determine_trigger_down_after_down_no_reminder_yet(self):
        last = SimpleNamespace(
            trigger_type="down", sent_at=datetime.now(UTC) - timedelta(minutes=30)
        )
        assert determine_trigger("down", last, datetime.now(UTC)) is None

    def test_determine_trigger_down_after_down_needs_reminder(self):
        last = SimpleNamespace(
            trigger_type="down", sent_at=datetime.now(UTC) - timedelta(hours=2)
        )
        assert determine_trigger("down", last, datetime.now(UTC)) == "reminder"

    def test_determine_trigger_down_after_reminder_needs_reminder(self):
        last = SimpleNamespace(
            trigger_type="reminder", sent_at=datetime.now(UTC) - timedelta(hours=2)
        )
        assert determine_trigger("down", last, datetime.now(UTC)) == "reminder"

    def test_determine_trigger_down_after_reminder_no_reminder_yet(self):
        last = SimpleNamespace(
            trigger_type="reminder", sent_at=datetime.now(UTC) - timedelta(minutes=30)
        )
        assert determine_trigger("down", last, datetime.now(UTC)) is None


class TestCompose:
    def test_compose_down(self):
        subject, body = _compose("http://test.com", "down")
        assert "[ALERT]" in subject
        assert "не отвечает" in body

    def test_compose_up(self):
        subject, body = _compose("http://test.com", "up")
        assert "[RESOLVED]" in subject
        assert "снова доступен" in body

    def test_compose_reminder(self):
        subject, body = _compose("http://test.com", "reminder")
        assert "[REMINDER]" in subject
        assert "по-прежнему не отвечает" in body


class TestDBHelpers:
    async def test_get_incident_data_found(self):
        session = AsyncMock()
        mock_result = SimpleNamespace(
            first=MagicMock(return_value=SimpleNamespace(id=10, url="http://x.com"))
        )
        session.execute.return_value = mock_result

        res = await _get_incident_data(session, 1)
        assert res == (10, "http://x.com")

    async def test_get_incident_data_not_found(self):
        session = AsyncMock()
        mock_result = SimpleNamespace(first=MagicMock(return_value=None))
        session.execute.return_value = mock_result

        res = await _get_incident_data(session, 1)
        assert res is None

    async def test_get_responsible_emails(self):
        session = AsyncMock()
        mock_result = [
            SimpleNamespace(email="a@a.com"),
            SimpleNamespace(email="b@b.com"),
        ]
        session.execute.return_value = mock_result

        res = await _get_responsible_emails(session, 10)
        assert res == ["a@a.com", "b@b.com"]


class TestNotifyIncident:
    async def test_notify_incident_no_incident(self):
        session = AsyncMock()
        with patch(
                "src.services.notification_service._get_incident_data",
                new=AsyncMock(return_value=None),
        ):
            await notify_incident(session, 1, "down")

    async def test_notify_incident_no_emails(self):
        session = AsyncMock()
        with patch(
                "src.services.notification_service._get_incident_data",
                new=AsyncMock(return_value=(10, "http://test.com")),
        ):
            with patch(
                    "src.services.notification_service._get_responsible_emails",
                    new=AsyncMock(return_value=[]),
            ):
                await notify_incident(session, 1, "down")

    async def test_notify_incident_success(self):
        session = AsyncMock()
        with patch(
                "src.services.notification_service._get_incident_data",
                new=AsyncMock(return_value=(10, "http://test.com")),
        ):
            with patch(
                    "src.services.notification_service._get_responsible_emails",
                    new=AsyncMock(return_value=["test@x.com"]),
            ):
                with patch(
                        "src.services.notification_service.NotificationRepository"
                ) as MockRepo:
                    mock_repo = AsyncMock()
                    mock_repo.get_last_sent_for_incident.return_value = None
                    mock_record = SimpleNamespace()
                    mock_repo.create.return_value = mock_record
                    MockRepo.return_value = mock_repo
                    with patch(
                            "src.services.notification_service._send_email", new=AsyncMock()
                    ) as mock_send:
                        await notify_incident(session, 1, "down")

                        mock_repo.create.assert_awaited_once()
                        mock_send.assert_awaited_once()
                        mock_repo.update.assert_awaited_once()
                        assert mock_repo.update.call_args[0][1]["status"] == "sent"

    async def test_notify_incident_send_fails(self):
        session = AsyncMock()
        with patch(
                "src.services.notification_service._get_incident_data",
                new=AsyncMock(return_value=(10, "http://test.com")),
        ):
            with patch(
                    "src.services.notification_service._get_responsible_emails",
                    new=AsyncMock(return_value=["test@x.com"]),
            ):
                with patch(
                        "src.services.notification_service.NotificationRepository"
                ) as MockRepo:
                    mock_repo = AsyncMock()
                    mock_repo.get_last_sent_for_incident.return_value = None
                    mock_record = SimpleNamespace()
                    mock_repo.create.return_value = mock_record
                    MockRepo.return_value = mock_repo
                    with patch(
                            "src.services.notification_service._send_email",
                            new=AsyncMock(side_effect=Exception("SMTP error")),
                    ):
                        await notify_incident(session, 1, "down")

                        mock_repo.create.assert_awaited_once()
                        mock_repo.update.assert_awaited_once()
                        assert mock_repo.update.call_args[0][1]["status"] == "failed"

    def test_send_sync(self):
        with patch("src.services.notification_service.smtplib.SMTP") as MockSMTP:
            mock_smtp_inst = MagicMock()
            MockSMTP.return_value.__enter__.return_value = mock_smtp_inst

            with patch("src.services.notification_service.settings") as mock_settings:
                mock_settings.email.smtp_from = "from@test.com"
                mock_settings.email.smtp_host = "localhost"
                mock_settings.email.smtp_port = 2525
                mock_settings.email.smtp_tls = True
                mock_settings.email.smtp_user = "user"
                mock_settings.email.smtp_password = "password"

                _send_sync("to@test.com", "Subj", "Body")

                mock_smtp_inst.starttls.assert_called_once()
                mock_smtp_inst.login.assert_called_once_with("user", "password")
                mock_smtp_inst.sendmail.assert_called_once()

                assert mock_smtp_inst.sendmail.call_args[0][0] == "from@test.com"
                assert mock_smtp_inst.sendmail.call_args[0][1] == ["to@test.com"]
