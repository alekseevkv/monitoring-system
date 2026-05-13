from enum import Enum
from datetime import datetime

from sqlalchemy import ForeignKey, Float, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, BaseModelMixin


class IncidentStatus(str, Enum):
    OPEN = "открыт"
    RESOLVED = "закрыт"


class Incident(Base, BaseModelMixin):
    __tablename__ = "incidents"

    monitoring_task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False, default=IncidentStatus.OPEN
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_by_check_id: Mapped[int | None] = mapped_column(
        ForeignKey("check_results.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_by_check_id: Mapped[int | None] = mapped_column(
        ForeignKey("check_results.id", ondelete="SET NULL"),
        nullable=True,
    )
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    monitoring_task = relationship("MonitoringTask", back_populates="incidents")