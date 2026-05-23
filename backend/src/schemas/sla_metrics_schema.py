from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

class ResponsibleAllSLARead(BaseModel):
    id: int
    name: str

    month_1: float | None
    month_2: float | None
    month_3: float | None
    month_4: float | None
    month_5: float | None
    month_6: float | None
    month_7: float | None
    month_8: float | None
    month_9: float | None
    month_10: float | None
    month_11: float | None
    month_12: float | None

class SLATableRead(BaseModel):
    months: list[date]
    items: list[ResponsibleAllSLARead] = []


class SLAMetricForMonth(BaseModel):
    id: int
    name: str
    sla_month: float | None
    achieved_target: bool
    successful_checks: int
    failed_checks: int
    total_checks: int
    success_rate: float
    incident_count: int
    total_downtime_seconds: float | None
    total_uptime_seconds: float | None
    avg_response_time_s: float | None
    min_response_time_s: float | None
    max_response_time_s: float | None