from fastapi import Depends

from src.repositories.monitoring_task import (
    MonitoringTaskRepository,
    get_monitoring_task_repository,
)
from src.schemas.monitoring_task_schema import (
    MonitoringTaskCreate,
    MonitoringTaskRead,
    MonitoringTaskUpdate,
)


class MonitoringTaskService:
    def __init__(self, repo: MonitoringTaskRepository):
        self.repo = repo

    async def create_task(self, data: MonitoringTaskCreate) -> MonitoringTaskRead:
        model = await self.repo.create(data)
        return MonitoringTaskRead.model_validate(model)

    async def get_task(self, task_id: int) -> MonitoringTaskRead:
        model = await self.repo.get_by_id(task_id)
        if not model:
            raise ValueError("Task not found")
        return MonitoringTaskRead.model_validate(model)

    async def list_tasks(
        self, skip: int = 0, limit: int = 50
    ) -> list[MonitoringTaskRead]:
        models = await self.repo.get_all(skip=skip, limit=limit)
        return [MonitoringTaskRead.model_validate(m) for m in models]

    async def update_task(
        self, task_id: int, data: MonitoringTaskUpdate
    ) -> MonitoringTaskRead:
        model = await self.repo.update(task_id, data)
        if not model:
            raise ValueError("Task not found")
        return MonitoringTaskRead.model_validate(model)

    async def delete_task(self, task_id: int) -> bool:
        return await self.repo.delete(task_id)


async def get_monitoring_task_service(
    repo: MonitoringTaskRepository = Depends(get_monitoring_task_repository),
) -> MonitoringTaskService:
    return MonitoringTaskService(repo)
