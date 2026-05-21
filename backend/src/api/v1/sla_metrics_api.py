from datetime import date
from fastapi import APIRouter, Depends, Query

from src.schemas.sla_metrics_schema import SLATableRead, SLAMetricForMonth
from src.services.sla_service import SLAService, get_sla_service

router = APIRouter()

@router.get("/", response_model=SLATableRead)
async def list_all_SLA(
    service: SLAService = Depends(get_sla_service),
):
    """SLA по всем сервисам за последние 12 месяцев"""
    return await service.get_all_sla_metrics()

@router.get("/{id}/", response_model=SLAMetricForMonth)
async def get_SLA(
    task_id: int,
    month: date = Query(
        default=None,
        description="Месяц для получения метрик. По умолчанию — прошлый месяц."
    ),
    service: SLAService = Depends(get_sla_service),
):
    """Все метрики сервиса за выбранный месяц"""
    if month is None:
        today = date.today()
        if today.month == 1:
            month = date(today.year - 1, 12, 1)
        else:
            month = date(today.year, today.month - 1, 1)

    return await service.get_sla_for_task_and_month(task_id, month)