from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DailyMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitoring_task_id: int
    date: date
    total_checks: int
    successful_checks: int
    failed_checks: int
    avg_response_time_s: float | None
    min_response_time_s: float | None
    max_response_time_s: float | None
    uptime_percentage: float
    sla_met: bool
    created_at: datetime
    updated_at: datetime


class SLASummaryRead(BaseModel):
    monitoring_task_id: int
    task_name: str
    sla_target: float = Field(..., description="Целевой SLA, %")

    uptime_last_day: float | None = Field(None, description="Uptime за последние сутки, %")
    uptime_last_week: float | None = Field(None, description="Uptime за последние 7 дней, %")
    uptime_last_month: float | None = Field(None, description="Uptime за последние 30 дней, %")

    sla_met_last_day: bool | None = Field(None, description="SLA выполнен за сутки")
    sla_met_last_week: bool | None = Field(None, description="SLA выполнен за 7 дней")
    sla_met_last_month: bool | None = Field(None, description="SLA выполнен за 30 дней")

    total_checks_last_month: int = Field(0, description="Всего проверок за 30 дней")
    failed_checks_last_month: int = Field(0, description="Провалено проверок за 30 дней")
