from fastapi import APIRouter, Depends, Query, status

from src.repositories.monitoring_task import MonitoringTaskRepository, get_monitoring_task_repository
from src.services.check_result_service import CheckResultService, get_check_result_service
from src.services.incident_service import IncidentService, get_incident_service
from src.helpers.orchestrator import Orchestrator, get_orchestrator
from src.schemas.check_result_schema import CheckResultRead, CheckResultListResponse
from src.schemas.incident_schema import IncidentListResponse, OpenIncidentListResponse, UptimeListResponse

router = APIRouter()


@router.get(
    "/monitoring-tasks/{task_id}/checks",
    status_code=status.HTTP_200_OK,
    response_model=CheckResultListResponse,
    summary="История проверок endpoint'а",
)
async def get_check_results(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: CheckResultService = Depends(get_check_result_service)
):
    return await service.get_by_task(task_id, skip, limit)


@router.get(
    "/monitoring-tasks/{task_id}/checks/latest",
    status_code=status.HTTP_200_OK,
    response_model=CheckResultRead,
    summary="Последняя проверка endpoint'а",
)
async def get_latest_check(
    task_id: int,
    service: CheckResultService = Depends(get_check_result_service)
):
    return await service.get_latest_by_task(task_id)


@router.get(
    "/monitoring-tasks/{task_id}/incidents",
    status_code=status.HTTP_200_OK,
    response_model=IncidentListResponse,
    summary="Список инцидентов для endpoint'а",
)
async def get_incidents(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: IncidentService = Depends(get_incident_service)
):
    return await service.get_by_task(task_id, skip, limit)


@router.get(
    "/open-incidents",
    status_code=status.HTTP_200_OK,
    response_model=OpenIncidentListResponse,
    summary="Список всех открытых инцидентов",
)
async def get_open_incidents(
    service: Orchestrator = Depends(get_orchestrator)
):
    return await service.get_open_incidents()


@router.get(
    "/uptime",
    status_code=status.HTTP_200_OK,
    response_model=UptimeListResponse,
    summary="Текущий uptime/длительность активного инцидента для активных задач"
)
async def get_uptime(
    service: IncidentService = Depends(get_incident_service),
    repo: MonitoringTaskRepository = Depends(get_monitoring_task_repository),
):
    tasks = await repo.get_active()
    return await service.get_uptime(tasks)