from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.incident import IncidentStatus
from src.services.incident_service import IncidentService
from src.schemas.incident_schema import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    UptimeListResponse,
)
from tests.helpers import fake_incident_row, fake_task_row
from tests.test_throttle import NOW

@pytest.fixture
def service(mock_incident_repo):
    mock_incident_repo.db = AsyncMock(spec=AsyncSession)
    return IncidentService(repo=mock_incident_repo)

@pytest.fixture
def notify():
    with patch(
        "src.services.incident_service.notify_incident", new=AsyncMock()
    ) as mocked:
        yield mocked


class TestCreate:
    async def test_create_success(self, service, mock_incident_repo):
        mock_incident_repo.create.return_value = fake_incident_row(id=3)

        result = await service.create(
            IncidentCreate(
                monitoring_task_id=10,
                status=IncidentStatus.OPEN,
                started_at=NOW,
                started_by_check_id=1,
                description="",
            )
        )

        assert isinstance(result, IncidentResponse)
        assert result.id == 3
        mock_incident_repo.create.assert_awaited_once()

    async def test_create_failure_raises_400(self, service, mock_incident_repo):
        mock_incident_repo.create.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.create(
                IncidentCreate(
                    monitoring_task_id=10,
                    status=IncidentStatus.OPEN,
                    started_at=NOW,
                    started_by_check_id=1,
                    description=None,
                )
            )

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetById:
    async def test_get_by_task_success(self, service, mock_incident_repo):
        rows = [fake_incident_row(id=1), fake_incident_row(id=2), fake_incident_row(id=3)]
        mock_incident_repo.get_by_task.return_value = (rows, 3)

        result = await service.get_by_task(task_id=10, skip=1, limit=5)

        assert isinstance(result, IncidentListResponse)
        assert [i.id for i in result.items] == [1, 2, 3]
        assert result.total == 3
    
    async def test_get_by_id_failure_raises_404(self, service, mock_incident_repo):
        mock_incident_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(999)

        assert exc.value.status_code == status.HTTP_404_NOT_FOUND


class TestGetOpen:
    async def test_get_open_success(self, service, mock_incident_repo):
        mock_incident_repo.get_open_for_task.return_value = fake_incident_row(id=2)
        result = await service.get_open_for_task(10)
        assert isinstance(result, IncidentResponse)
        assert result.id == 2
    
    async def test_get_open_empty(self, service, mock_incident_repo):
        mock_incident_repo.get_open.return_value = None
        assert await service.get_open_raw() == []

    async def test_get_open_rows(self, service, mock_incident_repo):
        mock_incident_repo.get_open.return_value = [fake_incident_row(id=1), fake_incident_row(id=2)]
        result = await service.get_open_raw()
        assert len(result) == 2
        assert isinstance(result[0], IncidentResponse)
        assert isinstance(result[1], IncidentResponse)

    async def test_get_open_for_task_none(self, service, mock_incident_repo):
        mock_incident_repo.get_open_for_task.return_value = None
        assert await service.get_open_for_task(10) is None


class TestUpdate:
    async def test_update_success(self, service, mock_incident_repo):
        mock_incident_repo.get_by_id.return_value = fake_incident_row(id=5)
        mock_incident_repo.update.return_value = fake_incident_row(
            id=5, status=IncidentStatus.RESOLVED, duration_seconds=12.0
        )

        result = await service.update(
            5, IncidentUpdate(status=IncidentStatus.RESOLVED, duration_seconds=12.0)
        )

        assert result.status == IncidentStatus.RESOLVED
        assert result.duration_seconds == 12.0
    
    async def test_empty_update(self, service, mock_incident_repo):
        mock_incident_repo.get_by_id.return_value = fake_incident_row(id=5)

        result = await service.update(5, IncidentUpdate())

        assert isinstance(result, IncidentResponse)
        assert result.id == 5
        mock_incident_repo.update.assert_not_awaited()

    async def test_update_failure_raises_400(self, service, mock_incident_repo):
        mock_incident_repo.get_by_id.return_value = fake_incident_row(id=5)
        mock_incident_repo.update.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.update(5, IncidentUpdate(status=IncidentStatus.RESOLVED))
        
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestResolve:
    async def test_resolve_success(
        self, service, mock_incident_repo
    ):
        open_incident = IncidentResponse.model_validate(
            fake_incident_row(id=8, started_at=NOW.replace(tzinfo=None), status=IncidentStatus.OPEN)
        )
        mock_incident_repo.get_by_id.return_value = fake_incident_row(id=8)
        mock_incident_repo.update.return_value = fake_incident_row(
            id=8, status=IncidentStatus.RESOLVED, resolved_by_check_id=55
        )

        result = await service.resolve(open_incident, resolved_by_check_id=55)

        assert result.status == IncidentStatus.RESOLVED
        _, sent_data = mock_incident_repo.update.await_args.args
        assert sent_data["status"] == IncidentStatus.RESOLVED
        assert sent_data["resolved_by_check_id"] == 55
        assert sent_data["duration_seconds"] > 0


class TestHandleIncident:
    async def test_open_incident(self, service, mock_incident_repo, notify):
        mock_incident_repo.get_open_for_task.return_value = None  # нет открытых
        mock_incident_repo.create.return_value = fake_incident_row(id=77)

        await service.handle_incident(
            task_id=10, check_id=500, is_success=False, error_message="500 error"
        )

        mock_incident_repo.create.assert_awaited_once()
        (sent,) = mock_incident_repo.create.await_args.args
        assert sent["monitoring_task_id"] == 10
        assert sent["status"] == IncidentStatus.OPEN
        assert sent["started_by_check_id"] == 500
        assert sent["description"] == "500 error"
        notify.assert_awaited_once()
        assert notify.await_args.args[1:] == (77, "down")

    async def test_renotify(self, service, mock_incident_repo, notify):
        mock_incident_repo.get_open_for_task.return_value = fake_incident_row(id=88)

        await service.handle_incident(
            task_id=10, check_id=501, is_success=False, error_message="still down"
        )

        mock_incident_repo.create.assert_not_awaited()
        notify.assert_awaited_once()
        assert notify.await_args.args[1:] == (88, "down")

    async def test_resolve(self, service, mock_incident_repo, notify):
        open_row = fake_incident_row(id=88, status=IncidentStatus.OPEN)
        mock_incident_repo.get_open_for_task.return_value = open_row
        mock_incident_repo.get_by_id.return_value = open_row
        mock_incident_repo.update.return_value = fake_incident_row(
            id=88, status=IncidentStatus.RESOLVED, resolved_by_check_id=502
        )

        await service.handle_incident(
            task_id=10, check_id=502, is_success=True, error_message=None
        )

        mock_incident_repo.update.assert_awaited_once()
        _, sent_data = mock_incident_repo.update.await_args.args
        assert sent_data["status"] == IncidentStatus.RESOLVED
        assert sent_data["resolved_by_check_id"] == 502
        notify.assert_awaited_once()
        assert notify.await_args.args[1:] == (88, "up")

    async def test_success_with_no_open_incidents(self, service, mock_incident_repo, notify):
        mock_incident_repo.get_open_for_task.return_value = None # нет открытых

        await service.handle_incident(
            task_id=10, check_id=503, is_success=True, error_message=None
        )

        mock_incident_repo.create.assert_not_awaited()
        mock_incident_repo.update.assert_not_awaited()
        notify.assert_not_awaited()


class TestGetUptime:
    async def test_empty_tasks(self, service, mock_incident_repo):
        result = await service.get_uptime([])
        assert isinstance(result, UptimeListResponse)
        assert result.items == []
        mock_incident_repo.get_uptime_data.assert_not_awaited()

    async def test_task_with_open_incident(self, service, mock_incident_repo):
        task = fake_task_row(id=10, name="API", http_method="GET")
        open_incident = fake_incident_row(started_at=(NOW.replace(tzinfo=None) - timedelta(seconds=120)))
        mock_incident_repo.get_uptime_data.return_value = {
            10: {"open": open_incident, "last_resolved": None}
        }

        result = await service.get_uptime([task])

        item = result.items[0]
        assert item.monitoring_task_id == 10
        assert item.is_incident is True
        assert item.uptime_s is None
        assert item.incident_duration_s is not None and item.incident_duration_s > 0

    async def test_task_without_open_incident(self, service, mock_incident_repo):
        task = fake_task_row(id=10)
        last_resolved = fake_incident_row(
            status=IncidentStatus.RESOLVED,
            resolved_at=(NOW.replace(tzinfo=None) - timedelta(seconds=300)),
        )
        mock_incident_repo.get_uptime_data.return_value = {
            10: {"open": None, "last_resolved": last_resolved}
        }

        result = await service.get_uptime([task])

        item = result.items[0]
        assert item.is_incident is False
        assert item.incident_duration_s is None
        assert item.uptime_s is not None and item.uptime_s > 0

    async def test_task_without_incidents(self, service, mock_incident_repo):
        task = fake_task_row(id=10, created_at=(NOW.replace(tzinfo=None) - timedelta(seconds=600)))
        mock_incident_repo.get_uptime_data.return_value = {
            10: {"open": None, "last_resolved": None}
        }

        result = await service.get_uptime([task])

        item = result.items[0]
        assert item.is_incident is False
        assert item.uptime_s is not None and item.uptime_s > 0