from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.models.incident import IncidentStatus


class IncidentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    monitoring_task_id: int
    status: IncidentStatus
    started_at: datetime
    resolved_at: datetime | None
    started_by_check_id: int | None
    resolved_by_check_id: int | None
    duration_seconds: float | None
    description: str | None


class IncidentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    monitoring_task_id: int
    status: IncidentStatus
    started_at: datetime
    started_by_check_id: int | None
    description: str | None


class IncidentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IncidentStatus | None = None
    resolved_at: datetime | None = None
    resolved_by_check_id: int | None = None
    duration_seconds: float | None = None


class IncidentResponse(IncidentBase):
    id: int
    created_at: datetime
    updated_at: datetime


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    skip: int
    limit: int


class OpenIncidentResponse(IncidentCreate):
    id: int
    description: str | None = None
    monitoring_task_name: str | None
    monitoring_task_method: str | None


class OpenIncidentListResponse(BaseModel):
    items: list[OpenIncidentResponse]


class UptimeResponse(BaseModel):
    monitoring_task_id: int
    monitoring_task_name: str | None
    monitoring_task_method: str | None
    is_incident: bool
    uptime_s: float | None
    incident_duration_s: float | None


class UptimeListResponse(BaseModel):
    items: list[UptimeResponse]