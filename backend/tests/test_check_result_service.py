from unittest.mock import patch

import httpx
import pytest
from fastapi import HTTPException, status

from src.services.check_result_service import CheckResultService
from src.schemas.check_result_schema import (
    CheckResultCreate,
    CheckResultUpdate,
    CheckResultRead,
    CheckResultListResponse,
)
from tests.helpers import (
    fake_check_row,
    fake_task,
    fake_response,
    make_async_client,
)

@pytest.fixture
def service(mock_check_repo):
    return CheckResultService(repo=mock_check_repo)


class TestCreate:
    async def test_create_success(self, service, mock_check_repo):
        mock_check_repo.create.return_value = fake_check_row(id=3, monitoring_task_id=10)

        result = await service.create(CheckResultCreate(monitoring_task_id=10))

        assert isinstance(result, CheckResultRead)
        assert result.id == 3
        assert result.monitoring_task_id == 10
        mock_check_repo.create.assert_awaited_once_with({"monitoring_task_id": 10})

    async def test_create_failure_raises_400(self, service, mock_check_repo):
        mock_check_repo.create.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.create(CheckResultCreate(monitoring_task_id=10))

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetById:
    async def test_get_by_id_success(self, service, mock_check_repo):
        mock_check_repo.get_by_id.return_value = fake_check_row(id=3)

        result = await service.get_by_id(3)

        assert isinstance(result, CheckResultRead)
        assert result.id == 3

    async def test_get_by_id_failure_raises_400(self, service, mock_check_repo):
        mock_check_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(999)

        assert exc.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdate:
    async def test_update_success(self, service, mock_check_repo):
        mock_check_repo.get_by_id.return_value = fake_check_row(id=5)
        mock_check_repo.update.return_value = fake_check_row(
            id=5, is_success=False, status_code=500, error_message="error"
        )

        payload = CheckResultUpdate(
            is_success=False,
            status_code=500,
            response_time_s=None,
            response_headers=None,
            response_body_preview=None,
            error_message="error",
        )
        result = await service.update(5, payload)

        assert isinstance(result, CheckResultRead)
        assert result.is_success is False
        assert result.status_code == 500
        assert result.error_message == "error"
        mock_check_repo.update.assert_awaited_once()

    async def test_update_failure_raises_400(self, service, mock_check_repo):
        mock_check_repo.get_by_id.return_value = fake_check_row(id=5)
        mock_check_repo.update.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.update(5, CheckResultUpdate(is_success=True))

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_failure_raises_404(self, service, mock_check_repo):
        mock_check_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.update(5, CheckResultUpdate(is_success=True))

        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
        mock_check_repo.update.assert_not_awaited()


class TestQueries:
    async def test_get_by_task_success(self, service, mock_check_repo):
        rows = [fake_check_row(id=1), fake_check_row(id=2), fake_check_row(id=3)]
        mock_check_repo.get_by_task_id.return_value = (rows, 3)

        result = await service.get_by_task(task_id=10, skip=1, limit=5)

        assert isinstance(result, CheckResultListResponse)
        assert [i.id for i in result.items] == [1, 2, 3]
        assert result.total == 3
        assert result.skip == 1
        assert result.limit == 5
        mock_check_repo.get_by_task_id.assert_awaited_once_with(10, 1, 5)

    async def test_get_by_task_empty(self, service, mock_check_repo):
        mock_check_repo.get_by_task_id.return_value = ([], 0)

        result = await service.get_by_task(task_id=10, skip=0, limit=50)

        assert result.items == []
        assert result.total == 0

    async def test_get_latest_success(self, service, mock_check_repo):
        mock_check_repo.get_latest_by_task.return_value = fake_check_row(id=3)

        result = await service.get_latest_by_task(10)

        assert result.id == 3

    async def test_get_latest_failure_raises_404(self, service, mock_check_repo):
        mock_check_repo.get_latest_by_task.return_value = None

        with pytest.raises(HTTPException) as exc:
            await service.get_latest_by_task(10)

        assert exc.value.status_code == status.HTTP_404_NOT_FOUND


class TestPerformHttpCheck:
    async def test_success(self, service):
        cm, request_mock = make_async_client(
            request_return=fake_response(
                status_code=200, text="success", headers={"x-trace": "abc"}
            )
        )
        task = fake_task(
            expected_status_code=200,
            http_method="GET",
            headers={"Authorization": "Bearer secret"},
            body=None,
        )

        with patch("src.services.check_result_service.httpx.AsyncClient", return_value=cm):
            result = await service.perform_http_check(task)

        assert isinstance(result, CheckResultUpdate)
        assert result.is_success is True
        assert result.status_code == 200
        assert result.response_body_preview == "success"
        assert result.response_headers == {"x-trace": "abc"}
        assert result.error_message is None
        assert result.response_time_s is not None and result.response_time_s >= 0
        request_mock.assert_awaited_once()
        kwargs = request_mock.await_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://example.com/health"
        assert kwargs["headers"] == {"Authorization": "Bearer secret"}

    async def test_status_mismatch(self, service):
        cm, _ = make_async_client(request_return=fake_response(status_code=503, text="failure"))
        task = fake_task(expected_status_code=200)

        with patch("src.services.check_result_service.httpx.AsyncClient", return_value=cm):
            result = await service.perform_http_check(task)

        assert result.is_success is False
        assert result.status_code == 503
        assert "200" in result.error_message and "503" in result.error_message

    async def test_body_truncated_to_2048(self, service):
        cm, _ = make_async_client(
            request_return=fake_response(status_code=200, text="A" * 5000)
        )
        task = fake_task(expected_status_code=200)

        with patch("src.services.check_result_service.httpx.AsyncClient", return_value=cm):
            result = await service.perform_http_check(task)

        assert len(result.response_body_preview) == 2048

    async def test_timeout(self, service):
        cm, _ = make_async_client(request_side_effect=httpx.TimeoutException("timed out"))
        task = fake_task(timeout=3)

        with patch("src.services.check_result_service.httpx.AsyncClient", return_value=cm):
            result = await service.perform_http_check(task)

        assert result.is_success is False
        assert result.status_code is None
        assert result.response_headers is None
        assert result.error_message.startswith("Timeout after 3s")

    async def test_exception(self, service):
        cm, _ = make_async_client(request_side_effect=httpx.ConnectError("connection refused"))
        task = fake_task()

        with patch("src.services.check_result_service.httpx.AsyncClient", return_value=cm):
            result = await service.perform_http_check(task)

        assert result.is_success is False
        assert result.status_code is None
        assert "connection refused" in result.error_message