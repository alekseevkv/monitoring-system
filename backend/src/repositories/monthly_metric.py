from __future__ import annotations

from datetime import date

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.monthly_metric import MonthlyMetric


class MonthlyMetricRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> MonthlyMetric:
        metric = MonthlyMetric(**data)
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def update(self, metric_id: int, data: dict) -> MonthlyMetric | None:
        metric = await self.get_by_id(metric_id)
        if not metric:
            return None
        for key, value in data.items():
            setattr(metric, key, value)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_by_id(self, metric_id: int) -> MonthlyMetric | None:
        stmt = select(MonthlyMetric).where(MonthlyMetric.id == metric_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_task_and_month(
        self, task_id: int, year: int, month: int
    ) -> MonthlyMetric | None:
        month_start = date(year, month, 1)
        stmt = select(MonthlyMetric).where(
            and_(
                MonthlyMetric.monitoring_task_id == task_id,
                MonthlyMetric.metric_date == month_start,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_task_id(
        self, task_id: int, months: int = 12
    ) -> list[MonthlyMetric]:
        today = date.today()
        year = today.year
        month = today.month - months
        while month <= 0:
            month += 12
            year -= 1
        cutoff = date(year, month, 1)
        stmt = (
            select(MonthlyMetric)
            .where(
                and_(
                    MonthlyMetric.monitoring_task_id == task_id,
                    MonthlyMetric.metric_date >= cutoff,
                )
            )
            .order_by(MonthlyMetric.metric_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


async def get_monthly_metric_repository(
    db: AsyncSession = Depends(get_session),
) -> MonthlyMetricRepository:
    return MonthlyMetricRepository(db)
