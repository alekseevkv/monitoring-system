from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.schemas.monitoring_task_schema import (
    MonitoringTaskCreate,
    MonitoringTaskRead,
    MonitoringTaskUpdate,
)
from src.services.monitoring_task_service import (
    MonitoringTaskService,
    get_monitoring_task_service,
)
from src.repositories.monitoring_task import (
    MonitoringTaskRepository,
    get_monitoring_task_repository,
)
from src.helpers.monitoring_scheduler import monitoring_scheduler

router = APIRouter()


@router.post(
    "/", response_model=MonitoringTaskRead, status_code=status.HTTP_201_CREATED
)
async def create_task(
    data: MonitoringTaskCreate,
    repo: MonitoringTaskRepository = Depends(get_monitoring_task_repository),
    service: MonitoringTaskService = Depends(get_monitoring_task_service),
):
    task = await service.create_task(data)
    
    if task.is_active:
        task_model = await repo.get_by_id(task.id)
        if task_model:
            monitoring_scheduler.schedule_task(task_model)
    return task


@router.get("/", response_model=list[MonitoringTaskRead])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: MonitoringTaskService = Depends(get_monitoring_task_service),
):
    return await service.list_tasks(skip=skip, limit=limit)


@router.get("/{task_id}/", response_model=MonitoringTaskRead)
async def get_task(
    task_id: int,
    service: MonitoringTaskService = Depends(get_monitoring_task_service),
):
    try:
        return await service.get_task(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.put("/{task_id}/", response_model=MonitoringTaskRead)
async def update_task(
    task_id: int,
    data: MonitoringTaskUpdate,
    repo: MonitoringTaskRepository = Depends(get_monitoring_task_repository),
    service: MonitoringTaskService = Depends(get_monitoring_task_service),
):
    try:
        task = await service.update_task(task_id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_model = await repo.get_by_id(task_id)
    if task_model:
        if task_model.is_active:
            monitoring_scheduler.schedule_task(task_model)
        else:
            monitoring_scheduler.unschedule_task(task_id)
    return task


@router.delete("/{task_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    service: MonitoringTaskService = Depends(get_monitoring_task_service),
):
    try:
        deleted = await service.delete_task(task_id)
        monitoring_scheduler.unschedule_task(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
