from __future__ import annotations

import calendar
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.monthly_metric import MonthlyMetric

if TYPE_CHECKING:
    from src.repositories.check_result import CheckResultRepository


class MonthlyMetricRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(
        self,
        task_id: int,
        month_start: date,
        stats: dict,
        sla_target: float,
    ) -> MonthlyMetric:
        """Создаёт или обновляет запись агрегированных метрик за месяц.
        month_start — первое число месяца (например, 2026-05-01).
        """
        total = stats["total"]
        successful = stats["successful"]
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 100.0
        achieved_target = success_rate >= sla_target

        existing = await self.get_by_task_and_month(
            task_id, month_start.year, month_start.month
        )
        if existing:
            existing.total_checks = total
            existing.successful_checks = successful
            existing.failed_checks = failed
            existing.success_rate = success_rate
            existing.total_downtime_seconds = stats.get("total_downtime_seconds")
            existing.total_uptime_seconds = stats.get("total_uptime_seconds")
            existing.incident_count = stats.get("incident_count", 0)
            existing.avg_response_time_s = stats.get("avg_response_time")
            existing.min_response_time_s = stats.get("min_response_time")
            existing.max_response_time_s = stats.get("max_response_time")
            existing.achieved_target = achieved_target
            existing.sla_month = stats.get("sla_month")
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        metric = MonthlyMetric(
            monitoring_task_id=task_id,
            date=month_start,
            total_checks=total,
            successful_checks=successful,
            failed_checks=failed,
            success_rate=success_rate,
            total_downtime_seconds=stats.get("total_downtime_seconds"),
            total_uptime_seconds=stats.get("total_uptime_seconds"),
            incident_count=stats.get("incident_count", 0),
            avg_response_time_s=stats.get("avg_response_time"),
            min_response_time_s=stats.get("min_response_time"),
            max_response_time_s=stats.get("max_response_time"),
            achieved_target=achieved_target,
            sla_month=stats.get("sla_month"),
        )
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_by_task_and_month(
        self, task_id: int, year: int, month: int
    ) -> MonthlyMetric | None:
        month_start = date(year, month, 1)
        stmt = select(MonthlyMetric).where(
            and_(
                MonthlyMetric.monitoring_task_id == task_id,
                MonthlyMetric.date == month_start,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_task_id(
        self, task_id: int, months: int = 12
    ) -> list[MonthlyMetric]:
        """Возвращает записи за последние N месяцев."""
        today = date.today()
        # Первое число месяца N месяцев назад
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
                    MonthlyMetric.date >= cutoff,
                )
            )
            .order_by(MonthlyMetric.date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_sla_summary_for_task(
        self, task_id: int, sla_target: float
    ) -> dict:
        """Возвращает success_rate за последние 1/3/12 месяцев."""
        today = date.today()
        year_ago = date(today.year - 1, today.month, 1)

        stmt = select(MonthlyMetric).where(
            and_(
                MonthlyMetric.monitoring_task_id == task_id,
                MonthlyMetric.date >= year_ago,
            )
        )
        result = await self.db.execute(stmt)
        metrics = list(result.scalars().all())

        def _compute(months_back: int) -> tuple[float | None, bool | None]:
            year = today.year
            month = today.month - months_back
            while month <= 0:
                month += 12
                year -= 1
            cutoff = date(year, month, 1)
            relevant = [m for m in metrics if m.date >= cutoff]
            total = sum(m.total_checks for m in relevant)
            successful = sum(m.successful_checks for m in relevant)
            if total == 0:
                return None, None
            sr = successful / total * 100
            return round(sr, 4), sr >= sla_target

        sr_1, met_1 = _compute(1)
        sr_3, met_3 = _compute(3)
        sr_12, met_12 = _compute(12)

        total_year = sum(m.total_checks for m in metrics)
        failed_year = sum(m.failed_checks for m in metrics)

        return {
            "success_rate_last_month": sr_1,
            "success_rate_last_3_months": sr_3,
            "success_rate_last_year": sr_12,
            "achieved_target_last_month": met_1,
            "achieved_target_last_3_months": met_3,
            "achieved_target_last_year": met_12,
            "total_checks_last_year": total_year,
            "failed_checks_last_year": failed_year,
        }

    async def compute_and_upsert_for_month(
        self,
        task_id: int,
        year: int,
        month: int,
        sla_target: float,
        check_repo: CheckResultRepository,
    ) -> MonthlyMetric:
        """Пересчитывает агрегированные метрики за месяц из сырых проверок."""
        last_day = calendar.monthrange(year, month)[1]
        start = datetime(year, month, 1, 0, 0, 0)
        end = datetime(year, month, last_day, 23, 59, 59)
        stats = await check_repo.get_stats_for_period(task_id, start, end)
        return await self.upsert(task_id, date(year, month, 1), stats, sla_target)


async def get_monthly_metric_repository(
    db: AsyncSession = Depends(get_session),
) -> MonthlyMetricRepository:
    return MonthlyMetricRepository(db)
