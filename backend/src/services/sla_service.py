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
        last_12_months = self._get_last_12_months()
        start_date = last_12_months[0]
        models = await self.repo.get_sla_for_period(start_date)

        task_dict: dict[int, ResponsibleAllSLARead] = {}

        for m in models:
            task_id = m.monitoring_task_id
            if task_id not in task_dict:
                task_dict[task_id] = ResponsibleAllSLARead(
                    id=task_id,
                    name=m.monitoring_task.name if getattr(m, 'monitoring_task', None) else f"Task {task_id}",
                    sla={}
                )

            task_dict[task_id].sla[m.date] = m.sla_month

        #Если надо вернуть и пустые значения
        # for row in task_dict.values():
        #     for month in last_12_months:
        #         if month not in row.sla:
        #             row.sla[month] = None

        return SLATableRead(
            months=last_12_months,
            items=list(task_dict.values())
        )

    async def get_sla_for_task_and_month(self, task_id: int, month: date) -> SLAMetricForMonth:
        model = await self.repo.get_sla_for_task_month(task_id, month)
        print(model)
        if not model:
            raise HTTPException(status_code=404, detail="Нет SLA за выбранный месяц")

        return SLAMetricForMonth(
            id=model.monitoring_task_id,
            name=model.monitoring_task.name if model.monitoring_task else f"Task {model.monitoring_task_id}",
            date=model.date,
            sla_month=model.sla_month,
            achieved_target=model.achieved_target,
            success_rate=model.success_rate,
            incident_count=model.incident_count,
            total_downtime_seconds=model.total_downtime_seconds,
            total_uptime_seconds=model.total_uptime_seconds,
        )

async def get_sla_service(
    repo: SLAMetricRepository = Depends(get_sla_metrics_repository),
) -> SLAService:
    return SLAService(repo)