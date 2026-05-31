from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status

from src.helpers.orchestrator import Orchestrator
from src.models.incident import IncidentStatus
from src.schemas.check_result_schema import CheckResultCreate, CheckResultUpdate
from src.schemas.incident_schema import OpenIncidentListResponse, IncidentResponse
from tests.helpers import fake_check_row, fake_incident_row, fake_task_row
from tests.test_throttle import NOW

@pytest.fixture
def services():
    return {
        "check": AsyncMock(),
        "incident": AsyncMock(),
        "task": AsyncMock(),
    }

@pytest.fixture
def orchestrator(services):
    return Orchestrator(
        check_service=services["check"],
        incident_service=services["incident"],
        task_service=services["task"],
    )


class TestRunCheck:
    async def test_check_is_not_successful(self, orchestrator, services):
        task = fake_task_row(id=10)
        created = fake_check_row(id=200, monitoring_task_id=10)
        raw_check = CheckResultUpdate(is_success=False, status_code=500, error_message="500 error")
        updated = fake_check_row(
            id=200, monitoring_task_id=10, is_success=False, error_message="500 error"
        )

        services["check"].create.return_value = created
        services["check"].perform_http_check.return_value = raw_check
        services["check"].update.return_value = updated

        await orchestrator.run_check(task)

        # для task создается CheckResult
        services["check"].create.assert_awaited_once()
        (create_arg,) = services["check"].create.await_args.args
        assert isinstance(create_arg, CheckResultCreate)
        assert create_arg.monitoring_task_id == 10

        # для task выполняется HTTP-проверка
        services["check"].perform_http_check.assert_awaited_once_with(task)

        # CheckResult дополняется результатом проверки
        services["check"].update.assert_awaited_once_with(created.id, raw_check)

        # информация для сервиса инцидентов
        services["incident"].handle_incident.assert_awaited_once_with(
            task_id=10,
            check_id=updated.id,
            is_success=False,
            error_message="500 error",
        )

    async def test_check_is_successful(self, orchestrator, services):
        task = fake_task_row(id=11)
        services["check"].create.return_value = fake_check_row(id=201)
        services["check"].perform_http_check.return_value = CheckResultUpdate(
            is_success=True, status_code=200
        )
        services["check"].update.return_value = fake_check_row(
            id=201, is_success=True, error_message=None
        )

        await orchestrator.run_check(task)

        kwargs = services["incident"].handle_incident.await_args.kwargs
        assert kwargs["is_success"] is True
        assert kwargs["error_message"] is None


class TestGetOpenIncidents:
    async def test_get_open_empty(self, orchestrator, services):
        services["incident"].get_open_raw.return_value = []

        result = await orchestrator.get_open_incidents()

        assert isinstance(result, OpenIncidentListResponse)
        assert result.items == []
        services["task"].get_task.assert_not_awaited()

    async def test_get_open_success(self, orchestrator, services):
        incident = IncidentResponse.model_validate(
            fake_incident_row(
                id=1,
                monitoring_task_id=10,
                status=IncidentStatus.OPEN,
                started_at=NOW,
                started_by_check_id=99,
                description="error",
            )
        )
        services["incident"].get_open_raw.return_value = [incident]
        services["task"].get_task.return_value = fake_task_row(
            id=10, name="API", http_method="POST"
        )

        result = await orchestrator.get_open_incidents()

        assert len(result.items) == 1
        item = result.items[0]
        assert item.id == 1
        assert item.monitoring_task_id == 10
        assert item.monitoring_task_name == "API"
        assert item.monitoring_task_method == "POST"
        assert item.started_by_check_id == 99

    async def test_get_open_failure_raises_404(self, orchestrator, services):
        from src.schemas.incident_schema import IncidentResponse

        incident = IncidentResponse.model_validate(
            fake_incident_row(monitoring_task_id=404)
        )
        services["incident"].get_open_raw.return_value = [incident]
        services["task"].get_task.side_effect = ValueError("Task not found")

        with pytest.raises(HTTPException) as exc:
            await orchestrator.get_open_incidents()

        assert exc.value.status_code == status.HTTP_404_NOT_FOUND