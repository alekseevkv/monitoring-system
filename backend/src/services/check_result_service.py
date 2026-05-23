import time
from datetime import datetime

from fastapi import Depends, HTTPException, status
import httpx

from src.models.monitoring_task import MonitoringTask
from src.repositories.check_result import CheckResultRepository, get_check_result_repository
from src.schemas.check_result_schema import (
    CheckResultRead, CheckResultListResponse, CheckResultCreate, CheckResultUpdate
)

class CheckResultService:
    def __init__(self, repo: CheckResultRepository):
        self.repo = repo

    async def create(self, data: CheckResultCreate) -> CheckResultRead:
        model = await self.repo.create(data.model_dump())
        if not model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check result creation failed",
            )
        return CheckResultRead.model_validate(model)

    async def update(self, check_id: int, data: CheckResultUpdate) -> CheckResultRead:
        check = await self.get_by_id(check_id)
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}

        if not update_dict:
            return check

        updated_check = await self.repo.update(check_id, update_dict)
        if not updated_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check result update failed",
            )
        return CheckResultRead.model_validate(updated_check)

    async def get_by_id(self, check_id: int) -> CheckResultRead:
        model = await self.repo.get_by_id(check_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Check result not found",
            )
        return CheckResultRead.model_validate(model)

    async def get_by_task(self, task_id: int, skip: int, limit: int) -> CheckResultListResponse:
        models, total = await self.repo.get_by_task_id(task_id, skip, limit)
        return CheckResultListResponse(
            items=[CheckResultRead.model_validate(i) for i in models],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_latest_by_task(self, task_id: int) -> CheckResultRead:
        model = await self.repo.get_latest_by_task(task_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No checks found for this task",
            )
        return CheckResultRead.model_validate(model)

    async def get_stats_for_period(self, task_id: int, start: datetime, end: datetime) -> dict:
        return await self.repo.get_stats_for_period(task_id, start, end)

    async def get_first_check_time(self, task_id: int) -> datetime | None:
        return await self.repo.get_first_check_time(task_id)

    async def perform_http_check(self, task: MonitoringTask) -> CheckResultUpdate:
        start = time.perf_counter()
        try:
            # Запрос
            async with httpx.AsyncClient(
                timeout=task.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.request(
                    method=task.http_method,
                    url=str(task.url),
                    headers=task.headers or {},
                    json=task.body
                )
            response_time_s = round(float((time.perf_counter() - start)), 2)
            is_success = response.status_code == task.expected_status_code

            # Тело (не более 2048 символов)
            try:
                body_preview = response.text[:2048]
            except Exception:
                body_preview = None

            result_data = CheckResultUpdate(
                is_success=is_success,
                status_code=response.status_code,
                response_time_s=response_time_s,
                response_headers=dict(response.headers),
                response_body_preview=body_preview,
                error_message=None if is_success else (
                    f"Expected status {task.expected_status_code}, "
                    f"got {response.status_code}"
                )
            )
            return result_data

        # Таймаут
        except httpx.TimeoutException as exc:
            response_time_s = round(float((time.perf_counter() - start)), 2)
            result_data = CheckResultUpdate(
                is_success=False,
                status_code=None,
                response_time_s=response_time_s,
                response_headers=None,
                response_body_preview=None,
                error_message=f"Timeout after {task.timeout}s: {exc}"
            )
            return result_data

        # Другое исключение
        except Exception as exc:
            response_time_s = round(float((time.perf_counter() - start)), 2)
            result_data = CheckResultUpdate(
                is_success=False,
                status_code=None,
                response_time_s=response_time_s,
                response_headers=None,
                response_body_preview=None,
                error_message=str(exc),
            )
            return result_data
            
async def get_check_result_service(
    repo: CheckResultRepository = Depends(get_check_result_repository)
) -> CheckResultService:
    return CheckResultService(repo)