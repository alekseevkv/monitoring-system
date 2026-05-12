from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, BaseModelMixin


class DailyMetric(Base, BaseModelMixin):
    __tablename__ = "daily_metrics"
    __table_args__ = (
        UniqueConstraint("monitoring_task_id", "date", name="uq_daily_metric_task_date"),
    )

    monitoring_task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    total_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    avg_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)

    uptime_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    sla_met: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True) #??

    monitoring_task = relationship("MonitoringTask", back_populates="daily_metrics")
