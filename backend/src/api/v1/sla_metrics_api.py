from datetime import date
from fastapi import APIRouter, Depends, Query, status

from src.schemas.sla_metrics_schema import SLATableRead, SLAMetricForMonth
from src.services.sla_service import SLAService, get_sla_service
from src.services.monthly_metric_service import MonthlyMetricService, get_monthly_metric_service

router = APIRouter()

@router.get("/", response_model=SLATableRead)
async def list_all_SLA(
    service: SLAService = Depends(get_sla_service),
):
    """SLA по всем сервисам за последние 12 месяцев"""
    return await service.get_all_sla_metrics()

@router.get("/{id}/", response_model=SLAMetricForMonth)
async def get_SLA(
    id: int,
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

    return await service.get_sla_for_task_and_month(id, month)

@router.post("/compute", status_code=status.HTTP_200_OK)
async def compute_all_sla_metrics(
    service: MonthlyMetricService = Depends(get_monthly_metric_service),
):
    """Перерасчет сырых метрик для SLA"""
    processed_count = await service.compute_for_all_tasks()
    return {"message": f"Успешно агрегированы метрики {processed_count} сервисов за предыдуший месяц"}