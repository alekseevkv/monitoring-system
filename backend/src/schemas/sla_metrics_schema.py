from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

class ResponsibleAllSLARead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sla: dict[date, float | None]

class SLATableRead(BaseModel):
    months: list[date]
    items: list[ResponsibleAllSLARead] = []


class SLAMetricForMonth(BaseModel):
    id: int
    name: str
    sla_month: float | None
    achieved_target: bool
    success_rate: float
    incident_count: int
    total_downtime_seconds: float | None
    total_uptime_seconds: float | None
