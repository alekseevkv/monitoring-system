import calendar
from datetime import date, datetime

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.incident import Incident
from src.repositories.monitoring_task import MonitoringTaskRepository, get_monitoring_task_repository
from src.repositories.monthly_metric import MonthlyMetricRepository, get_monthly_metric_repository
from src.schemas.monthly_metric_schema import MonthlyMetricRead
from src.services.check_result_service import CheckResultService, get_check_result_service


class MonthlyMetricService:
    def __init__(
        self,
        repo: MonthlyMetricRepository,
        task_repo: MonitoringTaskRepository,
        check_service: CheckResultService,
        db: AsyncSession,
    ):
        self.repo = repo
        self.task_repo = task_repo
        self.check_service = check_service
        self.db = db

    async def get_by_task(self, task_id: int, months: int = 12) -> list[MonthlyMetricRead]:
        models = await self.repo.get_by_task_id(task_id, months)
        return [MonthlyMetricRead.model_validate(m) for m in models]

    async def compute_for_month(
        self, task_id: int, year: int | None = None, month: int | None = None
    ) -> MonthlyMetricRead:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if year is None or month is None:
            today = date.today()
            month = today.month - 1
            year = today.year
            if month == 0:
                month = 12
                year -= 1

        last_day = calendar.monthrange(year, month)[1]
        month_start_dt = datetime(year, month, 1, 0, 0, 0)
        month_end_dt = datetime(year, month, last_day, 23, 59, 59)

        check_stats = await self.check_service.get_stats_for_period(task_id, month_start_dt, month_end_dt)
        first_check_dt = await self.check_service.get_first_check_time(task_id)

        inc_row = (
            await self.db.execute(
                select(
                    func.count(Incident.id).label("count"),
                    func.sum(Incident.duration_seconds).label("total_downtime"),
                ).where(
                    and_(
                        Incident.monitoring_task_id == task_id,
                        Incident.started_at >= month_start_dt,
                        Incident.started_at <= month_end_dt,
                    )
                )
            )
        ).one()

        monitoring_start = (
            first_check_dt if first_check_dt and first_check_dt > month_start_dt else month_start_dt
        )
        total_time = (month_end_dt - monitoring_start).total_seconds()
        total_downtime = float(inc_row.total_downtime) if inc_row.total_downtime else 0.0
        total_uptime = max(0.0, total_time - total_downtime)

        successful = check_stats["successful"]
        failed = check_stats["total"] - successful
        py_sla_month = (
            total_uptime / (total_uptime + total_downtime) * 100
            if (total_uptime + total_downtime) > 0
            else 100.0
        )
        achieved_target = py_sla_month >= task.sla_target

        data = {
            "monitoring_task_id": task_id,
            "metric_date": date(year, month, 1),
            "successful_checks": successful,
            "failed_checks": failed,
            "total_downtime_seconds": total_downtime,
            "total_uptime_seconds": total_uptime,
            "incident_count": inc_row.count or 0,
            "avg_response_time_s": check_stats.get("avg_response_time"),
            "min_response_time_s": check_stats.get("min_response_time"),
            "max_response_time_s": check_stats.get("max_response_time"),
            "achieved_target": achieved_target,
        }

        existing = await self.repo.get_by_task_and_month(task_id, year, month)
        model = await self.repo.update(existing.id, data) if existing else await self.repo.create(data)
        return MonthlyMetricRead.model_validate(model)

    async def get_sla_summary(self, task_id: int) -> dict:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        metrics = await self.repo.get_by_task_id(task_id, months=12)
        today = date.today()

        def _compute(months_back: int) -> tuple[float | None, bool | None]:
            year = today.year
            month = today.month - months_back
            while month <= 0:
                month += 12
                year -= 1
            cutoff = date(year, month, 1)
            relevant = [m for m in metrics if m.metric_date >= cutoff]
            total = sum(m.total_checks for m in relevant)
            successful = sum(m.successful_checks for m in relevant)
            if total == 0:
                return None, None
            sr = successful / total * 100
            return round(sr, 4), sr >= task.sla_target

        sr_1, met_1 = _compute(1)
        sr_3, met_3 = _compute(3)
        sr_12, met_12 = _compute(12)

        return {
            "success_rate_last_month": sr_1,
            "success_rate_last_3_months": sr_3,
            "success_rate_last_year": sr_12,
            "achieved_target_last_month": met_1,
            "achieved_target_last_3_months": met_3,
            "achieved_target_last_year": met_12,
            "total_checks_last_year": sum(m.total_checks for m in metrics),
            "failed_checks_last_year": sum(m.failed_checks for m in metrics),
        }


async def get_monthly_metric_service(
    repo: MonthlyMetricRepository = Depends(get_monthly_metric_repository),
    task_repo: MonitoringTaskRepository = Depends(get_monitoring_task_repository),
    check_service: CheckResultService = Depends(get_check_result_service),
    db: AsyncSession = Depends(get_session),
) -> MonthlyMetricService:
    return MonthlyMetricService(repo, task_repo, check_service, db)
