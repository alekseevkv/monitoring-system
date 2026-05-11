from datetime import datetime

from sqlalchemy import func
from sqlalchemy import Boolean, Float, String, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    monitoring_task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    check_timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    # Результат
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Сырые данные ответа
    response_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_body_preview: Mapped[str | None] = mapped_column(
        String(2048), nullable=True, doc="Первые 2048 символов тела ответа"
    )
    # Детали ошибки (если есть)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    monitoring_task = relationship("MonitoringTask", back_populates="check_results")