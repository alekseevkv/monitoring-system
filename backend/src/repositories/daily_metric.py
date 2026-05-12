from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.daily_metric import DailyMetric

if TYPE_CHECKING:
    from src.repositories.check_result import CheckResultRepository


class DailyMetricRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(
        self,
        task_id: int,
        metric_date: date,
        stats: dict,
        sla_target: float,
    ) -> DailyMetric:
        """Создаёт или обновляет запись агрегированных метрик за день."""
        total = stats["total"]
        successful = stats["successful"]
        failed = total - successful
        uptime = (successful / total * 100) if total > 0 else 100.0
        sla_met = uptime >= sla_target

        existing = await self.get_by_task_and_date(task_id, metric_date)
        if existing:
            existing.total_checks = total
            existing.successful_checks = successful
            existing.failed_checks = failed
            existing.avg_response_time_s = stats.get("avg_response_time")
            existing.min_response_time_s = stats.get("min_response_time")
            existing.max_response_time_s = stats.get("max_response_time")
            existing.uptime_percentage = uptime
            existing.sla_met = sla_met
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        metric = DailyMetric(
            monitoring_task_id=task_id,
            date=metric_date,
            total_checks=total,
            successful_checks=successful,
            failed_checks=failed,
            avg_response_time_s=stats.get("avg_response_time"),
            min_response_time_s=stats.get("min_response_time"),
            max_response_time_s=stats.get("max_response_time"),
            uptime_percentage=uptime,
            sla_met=sla_met,
        )
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_by_task_and_date(
        self, task_id: int, metric_date: date
    ) -> DailyMetric | None:
        stmt = select(DailyMetric).where(
            and_(
                DailyMetric.monitoring_task_id == task_id,
                DailyMetric.date == metric_date,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_task_id(
        self, task_id: int, days: int = 30
    ) -> list[DailyMetric]:
        cutoff = date.today() - timedelta(days=days)
        stmt = (
            select(DailyMetric)
            .where(
                and_(
                    DailyMetric.monitoring_task_id == task_id,
                    DailyMetric.date >= cutoff,
                )
            )
            .order_by(DailyMetric.date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_sla_summary_for_task(
        self, task_id: int, sla_target: float
    ) -> dict:
        """Вычисляет uptime за 1/7/30 дней из агрегированных данных."""
        today = date.today()
        month_ago = today - timedelta(days=30)

        stmt = (
            select(DailyMetric)
            .where(
                and_(
                    DailyMetric.monitoring_task_id == task_id,
                    DailyMetric.date >= month_ago,
                    DailyMetric.date <= today,
                )
            )
        )
        result = await self.db.execute(stmt)
        metrics = list(result.scalars().all())

        def _compute(days_back: int) -> tuple[float | None, bool | None]:
            cutoff = today - timedelta(days=days_back)
            relevant = [m for m in metrics if m.date >= cutoff]
            total = sum(m.total_checks for m in relevant)
            successful = sum(m.successful_checks for m in relevant)
            if total == 0:
                return None, None
            uptime = successful / total * 100
            return round(uptime, 4), uptime >= sla_target

        uptime_1, met_1 = _compute(1)
        uptime_7, met_7 = _compute(7)
        uptime_30, met_30 = _compute(30)

        total_month = sum(m.total_checks for m in metrics)
        failed_month = sum(m.failed_checks for m in metrics)

        return {
            "uptime_last_day": uptime_1,
            "uptime_last_week": uptime_7,
            "uptime_last_month": uptime_30,
            "sla_met_last_day": met_1,
            "sla_met_last_week": met_7,
            "sla_met_last_month": met_30,
            "total_checks_last_month": total_month,
            "failed_checks_last_month": failed_month,
        }

    async def compute_and_upsert_for_date(
        self,
        task_id: int,
        metric_date: date,
        sla_target: float,
        check_repo: CheckResultRepository,
    ) -> DailyMetric:
        """Пересчитывает агрегированные метрики за день из сырых проверок."""
        start = datetime.combine(metric_date, time.min)
        end = datetime.combine(metric_date, time.max)
        stats = await check_repo.get_stats_for_period(task_id, start, end)
        return await self.upsert(task_id, metric_date, stats, sla_target)


async def get_daily_metric_repository(
    db: AsyncSession = Depends(get_session),
) -> DailyMetricRepository:
    return DailyMetricRepository(db)
