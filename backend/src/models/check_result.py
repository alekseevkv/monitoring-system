from sqlalchemy import Boolean, Float, String, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, BaseModelMixin


class CheckResult(Base, BaseModelMixin):
    __tablename__ = "check_results"

    monitoring_task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    # Результат
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Сырые данные ответа
    response_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_body_preview: Mapped[str | None] = mapped_column(
        String(2048), nullable=True, doc="Первые 2048 символов тела ответа"
    )
    # Детали ошибки (если есть)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    monitoring_task = relationship("MonitoringTask", back_populates="check_results")