from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.monitoring_task import MonitoringTask
from src.schemas.monitoring_task_schema import (
    MonitoringTaskCreate,
    MonitoringTaskUpdate,
)


class MonitoringTaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task_data: MonitoringTaskCreate) -> MonitoringTask:
        task = MonitoringTask(**task_data.model_dump())
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_by_id(self, task_id: int) -> MonitoringTask | None:
        stmt = select(MonitoringTask).where(MonitoringTask.id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[MonitoringTask]:
        stmt = (
            select(MonitoringTask)
            .order_by(MonitoringTask.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, task_id: int, data: MonitoringTaskUpdate
    ) -> MonitoringTask | None:
        instance = await self.get_by_id(task_id)
        if not instance:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(instance, field, value)

        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, task_id: int) -> bool:
        instance = await self.get_by_id(task_id)
        if not instance:
            return False
        await self.db.delete(instance)
        await self.db.commit()
        return True


async def get_monitoring_task_repository(
    db: AsyncSession = Depends(get_session),
) -> MonitoringTaskRepository:
    return MonitoringTaskRepository(db)
