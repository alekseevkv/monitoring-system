from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from src.models.incident import IncidentStatus
from src.models.monitoring_task import MonitoringTask
from .test_throttle import NOW

def fake_check_row(**overrides) -> SimpleNamespace:
    """Строка CheckResult ORM для CheckResultRead.model_validate"""
    data = dict(
        id=1,
        monitoring_task_id=10,
        is_success=True,
        status_code=200,
        response_time_s=0.12,
        response_headers={"content-type": "application/json"},
        response_body_preview="ok",
        error_message=None,
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def fake_incident_row(**overrides) -> SimpleNamespace:
    """Строка Incident ORM для IncidentResponse.model_validate"""
    data = dict(
        id=1,
        monitoring_task_id=10,
        status=IncidentStatus.OPEN,
        started_at=NOW.replace(tzinfo=None),
        resolved_at=None,
        started_by_check_id=100,
        resolved_by_check_id=None,
        duration_seconds=None,
        description="error",
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def fake_task_row(**overrides) -> SimpleNamespace:
    """Строка MonitoringTask ORM для perform_http_check / get_uptime"""
    data = dict(
        id=10,
        name="Сервис example.com",
        description=None,
        is_active=True,
        url="https://example.com/health",
        http_method="GET",
        headers=None,
        body=None,
        timeout=5,
        expected_status_code=200,
        created_at=NOW,
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def real_task_row(**overrides) -> MonitoringTask:
    """MonitoringTask для _make_trigger / schedule_task"""
    data = dict(
        id=10,
        name="Сервис example.com",
        url="https://example.com/health",
        is_active=True,
        cron_expression=None,
        check_interval_seconds=300,
    )
    data.update(overrides)
    return MonitoringTask(**data)


def fake_response(status_code=200, text="ok", headers=None) -> SimpleNamespace:
    return SimpleNamespace(
        status_code=status_code,
        text=text,
        headers=headers if headers is not None else {"server": "nginx"},
    )


def make_async_client(request_return=None, request_side_effect=None):
    """Мок httpx.AsyncClient. Возвращает (context_manager_mock, request_mock)"""
    request_mock = AsyncMock(
        return_value=request_return, side_effect=request_side_effect
    )
    client = MagicMock()
    client.request = request_mock

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm, request_mock


def make_session_maker(session):
    """Мок async_session_maker"""
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)
    return MagicMock(return_value=cm)