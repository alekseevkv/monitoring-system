from datetime import date
from fastapi import Depends, HTTPException

from src.repositories.sla_metrics import get_sla_metrics_repository, SLAMetricRepository
from src.schemas.sla_metrics_schema import SLATableRead, ResponsibleAllSLARead, SLAMetricForMonth


class SLAService:
    def __init__(self, repo: SLAMetricRepository):
        self.repo = repo

    def _get_last_12_months(self) -> list[date]:
        today = date.today()

        if today.month == 1:
            current = date(today.year - 1, 12, 1)
        else:
            current = date(today.year, today.month - 1, 1)

        months: list[date] = []

        for _ in range(12):
            months.append(current)
            if current.month == 1:
                current = current.replace(year=current.year - 1, month=12)
            else:
                current = current.replace(month=current.month - 1)

        months.reverse()
        return months

    async def get_all_sla_metrics(self) -> SLATableRead:
        last_12_months = self._get_last_12_months()   # список из 12 месяцев
        start_date = last_12_months[0]

        models = await self.repo.get_sla_for_period(start_date)

        task_dict = {}

        for m in models:
            task_id = m.monitoring_task_id

            if task_id not in task_dict:
                task_dict[task_id] = {
                    "id": task_id,
                    "name": m.monitoring_task.name if m.monitoring_task else f"Task {task_id}",
                    "month_1": None,
                    "month_2": None,
                    "month_3": None,
                    "month_4": None,
                    "month_5": None,
                    "month_6": None,
                    "month_7": None,
                    "month_8": None,
                    "month_9": None,
                    "month_10": None,
                    "month_11": None,
                    "month_12": None,
                }

            for i, month in enumerate(last_12_months, start=1):
                if month == m.metric_date:
                    task_dict[task_id][f"month_{i}"] = m.sla_month
                    break

        items = [ResponsibleAllSLARead(**data) for data in task_dict.values()]
        return SLATableRead(
            months=last_12_months,
            items=items
        )

    async def get_sla_for_task_and_month(self, task_id: int, month: date) -> SLAMetricForMonth:
        model = await self.repo.get_sla_for_task_month(task_id, month)
        print(model)
        if not model:
            raise HTTPException(status_code=404, detail="Нет SLA за выбранный месяц")

        return SLAMetricForMonth(
            id=model.monitoring_task_id,
            name=model.monitoring_task.name if model.monitoring_task else f"Task {model.monitoring_task_id}",
            sla_month=model.sla_month,
            achieved_target=model.achieved_target,
            success_rate=model.success_rate,
            failed_checks = model.failed_checks,
            total_checks = model.total_checks,
            successful_checks = model.successful_checks,
            incident_count=model.incident_count,
            total_downtime_seconds=model.total_downtime_seconds,
            total_uptime_seconds=model.total_uptime_seconds,
            avg_response_time_s = model.avg_response_time_s,
            min_response_time_s = model.min_response_time_s,
            max_response_time_s = model.max_response_time_s
        )

async def get_sla_service(
    repo: SLAMetricRepository = Depends(get_sla_metrics_repository),
) -> SLAService:
    return SLAService(repo)