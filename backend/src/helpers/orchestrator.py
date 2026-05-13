from fastapi import Depends, HTTPException, status

from src.models.monitoring_task import MonitoringTask
from src.schemas.check_result_schema import CheckResultCreate
from src.schemas.incident_schema import OpenIncidentResponse, OpenIncidentListResponse
from src.services.check_result_service import CheckResultService, get_check_result_service
from src.services.incident_service import IncidentService, get_incident_service
from src.services.monitoring_task_service import MonitoringTaskService, get_monitoring_task_service


class Orchestrator:
    def __init__(
        self,
        check_service: CheckResultService,
        incident_service: IncidentService,
        task_service: MonitoringTaskService,
    ):
        self.check_service = check_service
        self.incident_service = incident_service
        self.task_service = task_service

    async def run_check(self, task: MonitoringTask) -> None:
        """
        Выполняет одну проверку endpoint'а, сохраняет сырые данные (CheckResult),
        управляет инцидентами (открытие / закрытие).
        """
        # Создаем CheckResult (время проверки = created_at)
        check = await self.check_service.create(
            CheckResultCreate(monitoring_task_id=task.id)
        )
        # Выполняем запрос
        check_result_update = await self.check_service.perform_http_check(task)
        # Сохраняем сырые данные
        check = await self.check_service.update(check.id, check_result_update)
        # Открываем новый инцидент при ошибке или закрываем существующий
        await self.incident_service.handle_incident(
            task_id=task.id,
            check_id=check.id,
            is_success=check.is_success,
            error_message=check.error_message,
        )

    async def get_open_incidents(self) -> OpenIncidentListResponse:
        incidents = await self.incident_service.get_open_raw()
        if not incidents:
            return OpenIncidentListResponse(items=[])

        items = []
        for incident in incidents:
            try:
                task = await self.task_service.get_task(incident.monitoring_task_id)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            items.append(
                OpenIncidentResponse(
                    id=incident.id,
                    monitoring_task_id=incident.monitoring_task_id,
                    status=incident.status,
                    started_at=incident.started_at,
                    started_by_check_id=incident.started_by_check_id,
                    description=incident.description,
                    monitoring_task_name=task.name,
                    monitoring_task_method=task.http_method,
                )
            )
        return OpenIncidentListResponse(items=items)


async def get_orchestrator(
    check_service: CheckResultService = Depends(get_check_result_service),
    incident_service: IncidentService = Depends(get_incident_service),
    task_service: MonitoringTaskService = Depends(get_monitoring_task_service),
) -> Orchestrator:
    return Orchestrator(check_service, incident_service, task_service)