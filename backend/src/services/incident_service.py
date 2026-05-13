from typing import Sequence
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status

from src.models.incident import IncidentStatus
from src.repositories.incidents import IncidentRepository, get_incident_repository
from src.schemas.incident_schema import (
    IncidentListResponse, IncidentResponse, IncidentCreate, IncidentUpdate
)

class IncidentService:
    def __init__(self, repo: IncidentRepository):
        self.repo = repo

    async def create(self, data: IncidentCreate) -> IncidentResponse:
        model = await self.repo.create(data.model_dump())
        if not model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incident creation failed",
            )
        return IncidentResponse.model_validate(model)

    async def update(self, incident_id: int, data: IncidentUpdate) -> IncidentResponse:
        incident = await self.get_by_id(incident_id)
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}

        if not update_dict:
            return incident

        updated_incident = await self.repo.update(incident_id, update_dict)
        if not updated_incident:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incident update failed",
            )
        return IncidentResponse.model_validate(updated_incident)

    async def get_by_id(self, incident_id: int) -> IncidentResponse:
        model = await self.repo.get_by_id(incident_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )
        return IncidentResponse.model_validate(model)
    
    async def get_by_task(self, task_id: int, skip: int, limit: int) -> IncidentListResponse:
        models, total = await self.repo.get_by_task(task_id, skip, limit)
        return IncidentListResponse(
            items=[IncidentResponse.model_validate(i) for i in models],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_open_raw(self) -> Sequence[IncidentResponse]:
        # открытые инциденты без обогащения данными задач
        models = await self.repo.get_open()
        if not models:
            return []
        return [IncidentResponse.model_validate(m) for m in models]
    
    async def get_open_for_task(self, task_id: int) -> IncidentResponse | None:
        model = await self.repo.get_open_for_task(task_id)
        if not model:
            return None
        return IncidentResponse.model_validate(model)

    async def resolve(self, incident: IncidentResponse, resolved_by_check_id: int) -> IncidentResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        update_data = IncidentUpdate(
            status=IncidentStatus.RESOLVED,
            resolved_at=now,
            resolved_by_check_id=resolved_by_check_id,
            duration_seconds=float(
                (now - incident.started_at).total_seconds()
            )
        )
        res = await self.update(incident.id, update_data)
        return res
    
    async def handle_incident(
        self, task_id: int, check_id: int, is_success: bool, error_message: str | None
    ) -> None:
        """Открывает новый инцидент при ошибке или закрывает существующий"""
        # Последний открытый инцидент для задачи
        open_incident = await self.get_open_for_task(task_id)

        if not is_success:
            if open_incident is None:
                # Открываем новый инцидент
                create_data = IncidentCreate(
                    monitoring_task_id=task_id,
                    status=IncidentStatus.OPEN,
                    started_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    started_by_check_id=check_id,
                    description=error_message
                )
                await self.create(create_data)

        else:
            if open_incident is not None:
                # Закрываем инцидент
                await self.resolve(open_incident, check_id)

async def get_incident_service(
    repo: IncidentRepository = Depends(get_incident_repository),
) -> IncidentService:
    return IncidentService(repo)