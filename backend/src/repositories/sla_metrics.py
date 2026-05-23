from fastapi import Depends
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import date

from src.database import get_session
from src.models.monthly_metric import MonthlyMetric

class SLAMetricRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sla_for_period(self, start_date: date):
        stmt = (
            select(MonthlyMetric)
            .options(selectinload(MonthlyMetric.monitoring_task))
            .where(MonthlyMetric.metric_date >= start_date)
            .order_by(MonthlyMetric.monitoring_task_id, MonthlyMetric.metric_date)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_sla_for_task_month(self, task_id: int, month: date):
        stmt = (
            select(MonthlyMetric)
            .options(selectinload(MonthlyMetric.monitoring_task))
            .where(
                MonthlyMetric.monitoring_task_id == task_id,
                extract('year', MonthlyMetric.metric_date) == month.year,
                extract('month', MonthlyMetric.metric_date) == month.month
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


async def get_sla_metrics_repository(
    db: AsyncSession = Depends(get_session),
) -> SLAMetricRepository:
    return SLAMetricRepository(db)