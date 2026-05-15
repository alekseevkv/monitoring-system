from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_serializer


class ResponsiblePersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class ResponsiblePersonCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., min_length=1, max_length=255)


class ResponsiblePersonNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., min_length=1, max_length=255)


class MonitoringTaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Название сервиса")
    description: str | None = Field(None, description="Описание сервиса")
    is_active: bool = Field(True, description="Активен ли мониторинг")

    url: HttpUrl
    http_method: str = Field(
        "GET",
        pattern="^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$",
        description="Методы запроса",
    )
    headers: dict | None = Field(None, description="Кастомные HTTP-заголовки")
    body: dict | None = Field(None, description="Тело запроса")
    timeout: int = Field(30, ge=1, le=300, description="Таймаут в секундах")
    expected_status_code: int = Field(200, ge=100, le=599)

    sla_target: float = Field(
        99.9, ge=0.0, le=100.0, description="Целевая доступность в %"
    )
    check_interval_seconds: int = Field(
        300, ge=10, description="Интервал проверки в секундах"
    )
    cron_expression: str | None = Field(
        None, max_length=255, description="Cron-расписание"
    )

    @field_serializer("url")
    def serialize_url(self, value: HttpUrl) -> str:
        return str(value)


class MonitoringTaskCreate(MonitoringTaskBase):
    responsible_persons: list[ResponsiblePersonCreate] = Field(default_factory=list)


class MonitoringTaskRead(MonitoringTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    responsible_persons: list[ResponsiblePersonRead] = Field(default_factory=list)


class MonitoringTaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None
    url: HttpUrl | None = None
    http_method: str | None = Field(
        None, pattern="^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$"
    )
    headers: dict | None = None
    body: dict | None = None
    timeout: int | None = Field(None, ge=1, le=300)
    expected_status_code: int | None = Field(None, ge=100, le=599)
    sla_target: float | None = Field(None, ge=0.0, le=100.0)
    check_interval_seconds: int | None = Field(None, ge=10)
    cron_expression: str | None = Field(None, max_length=255)
    responsible_persons: list[ResponsiblePersonNested] | None = None

    @field_serializer("url")
    def serialize_url(self, value: HttpUrl) -> str:
        return str(value)
