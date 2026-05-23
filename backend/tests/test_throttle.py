"""Unit tests for notification throttle logic (no DB required)."""
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.services.notification_service import REMINDER_INTERVAL, determine_trigger


def make_notification(trigger_type: str, sent_at: datetime) -> MagicMock:
    n = MagicMock()
    n.trigger_type = trigger_type
    n.sent_at = sent_at
    return n


NOW = datetime(2026, 5, 15, 12, 0, 0, tzinfo=UTC)
RECENT = NOW - timedelta(minutes=30)
HOUR_AGO = NOW - REMINDER_INTERVAL - timedelta(seconds=1)


class TestDetermineTriggernNoHistory:
    def test_first_check_down(self):
        assert determine_trigger("down", None, NOW) == "down"

    def test_first_check_up(self):
        assert determine_trigger("up", None, NOW) is None


class TestDetermineTriggerDown:
    def test_state_change_up_to_down(self):
        last = make_notification("up", RECENT)
        assert determine_trigger("down", last, NOW) == "down"

    def test_already_down_no_reminder_yet(self):
        last = make_notification("down", RECENT)
        assert determine_trigger("down", last, NOW) is None

    def test_reminder_after_hour(self):
        last = make_notification("down", HOUR_AGO)
        assert determine_trigger("down", last, NOW) == "reminder"

    def test_reminder_interval_not_passed(self):
        last = make_notification("reminder", RECENT)
        assert determine_trigger("down", last, NOW) is None

    def test_reminder_after_previous_reminder(self):
        last = make_notification("reminder", HOUR_AGO)
        assert determine_trigger("down", last, NOW) == "reminder"


class TestDetermineTriggerUp:
    def test_recovery_after_down(self):
        last = make_notification("down", RECENT)
        assert determine_trigger("up", last, NOW) == "up"

    def test_recovery_after_reminder(self):
        last = make_notification("reminder", HOUR_AGO)
        assert determine_trigger("up", last, NOW) == "up"

    def test_already_up(self):
        last = make_notification("up", RECENT)
        assert determine_trigger("up", last, NOW) is None
