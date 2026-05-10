from sqlalchemy import JSON, Boolean, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, BaseModelMixin


class MonitoringTask(Base, BaseModelMixin):
    __tablename__ = "monitoring_tasks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Параметры HTTP-запроса
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    http_method: Mapped[str] = mapped_column(String(10), default="GET")
    headers: Mapped[dict | None] = mapped_column(JSON)
    timeout: Mapped[int] = mapped_column(Integer, default=30)
    expected_status_code: Mapped[int] = mapped_column(Integer, default=200)

    # SLA и расписание
    sla_target: Mapped[float] = mapped_column(Float, default=99.9)
    check_interval_seconds: Mapped[int] = mapped_column(Integer, default=300)
    cron_expression: Mapped[str | None] = mapped_column(String(255))

    # Ответственные и уведомления
    responsible_persons: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    notification_emails: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
