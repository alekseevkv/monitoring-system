from typing import Sequence
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.incident import Incident, IncidentStatus


class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Incident:
        incident = Incident(**data)
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def get_open(self) -> Sequence[Incident] | None:
        stmt = (
            select(Incident)
            .where(Incident.status == IncidentStatus.OPEN)
            .order_by(Incident.started_at.desc())
        )
        return (await self.db.execute(stmt)).scalars().all()

    async def get_open_for_task(self, task_id: int) -> Incident | None:
        stmt = (
            select(Incident)
            .where(
                Incident.monitoring_task_id == task_id,
                Incident.status == IncidentStatus.OPEN,
            )
            .order_by(Incident.started_at.desc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
    
    async def get_by_id(self, incident_id: int) -> Incident | None:
        stmt = select(Incident).where(Incident.id == incident_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, incident_id: int, data: dict) -> Incident | None:
        incident = await self.get_by_id(incident_id)
        if not incident:
            return None

        for key, value in data.items():
            setattr(incident, key, value)
        
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def resolve(
        self, incident: Incident, resolved_by_check_id: int
    ) -> Incident:
        now = datetime.now(timezone.utc)
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = now
        incident.resolved_by_check_id = resolved_by_check_id
        incident.duration_seconds = float(
            (now - incident.started_at.replace(tzinfo=timezone.utc)).total_seconds()
        )
        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def get_by_task(
        self, task_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[Incident], int]:
        count_stmt = (
            select(func.count())
            .select_from(Incident)
            .where(Incident.monitoring_task_id == task_id)
        )
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(Incident)
            .where(Incident.monitoring_task_id == task_id)
            .order_by(Incident.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total


async def get_incident_repository(
    db: AsyncSession = Depends(get_session),
) -> IncidentRepository:
    return IncidentRepository(db)
