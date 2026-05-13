from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_session
from src.models.monitoring_task import MonitoringTask
from src.models.responsible_person import ResponsiblePerson
from src.schemas.monitoring_task_schema import (
    MonitoringTaskCreate,
    MonitoringTaskUpdate,
)


class MonitoringTaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _with_persons(self):
        return selectinload(MonitoringTask.responsible_persons)

    async def create(self, task_data: MonitoringTaskCreate) -> MonitoringTask:
        task_dict = task_data.model_dump(exclude={"responsible_persons"})
        task = MonitoringTask(**task_dict)

        for person_data in task_data.responsible_persons:
            person = ResponsiblePerson(**person_data.model_dump())
            task.responsible_persons.append(person)

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        await self.db.refresh(task, attribute_names=["responsible_persons"])
        return task

    async def get_by_id(self, task_id: int) -> MonitoringTask | None:
        stmt = (
            select(MonitoringTask)
            .options(self._with_persons())
            .where(MonitoringTask.id == task_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[MonitoringTask]:
        stmt = (
            select(MonitoringTask)
            .options(self._with_persons())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, task_id: int, data: MonitoringTaskUpdate
    ) -> MonitoringTask | None:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        for field, value in data.model_dump(
            exclude_unset=True, exclude={"responsible_persons"}
        ).items():
            setattr(task, field, value)

        if data.responsible_persons is not None:
            new_persons_list = []

            for pd in data.responsible_persons:
                update_dict = pd.model_dump(exclude={"id"}, exclude_unset=True)
                if pd.id is not None:
                    existing = next(
                        (p for p in task.responsible_persons if p.id == pd.id), None
                    )
                    if existing:
                        for k, v in update_dict.items():
                            setattr(existing, k, v)
                        new_persons_list.append(existing)
                    else:
                        new_persons_list.append(ResponsiblePerson(**update_dict))
                else:
                    new_persons_list.append(ResponsiblePerson(**update_dict))

            task.responsible_persons = new_persons_list

        await self.db.commit()
        await self.db.refresh(task, attribute_names=["responsible_persons"])
        return task

    async def delete(self, task_id: int) -> bool:
        task = await self.get_by_id(task_id)
        if not task:
            return False
        await self.db.delete(task)
        await self.db.commit()
        return True


async def get_monitoring_task_repository(
    db: AsyncSession = Depends(get_session),
) -> MonitoringTaskRepository:
    return MonitoringTaskRepository(db)
