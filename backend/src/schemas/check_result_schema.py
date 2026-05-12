from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CheckResultCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    monitoring_task_id: int = Field(..., description="ID задачи мониторинга")
    is_success: bool = Field(..., description="Успешна ли проверка")
    status_code: int | None = Field(None, ge=100, le=599, description="HTTP статус-код ответа")
    response_time_s: float | None = Field(None, ge=0, description="Время ответа в секундах")
    response_headers: dict | None = Field(None, description="Заголовки ответа")
    response_body_preview: str | None = Field(
        None, max_length=2048, description="Первые 2048 символов тела ответа"
    )
    error_message: str | None = Field(None, description="Сообщение об ошибке")


class CheckResultRead(CheckResultCreate):
    id: int
    created_at: datetime
    updated_at: datetime
