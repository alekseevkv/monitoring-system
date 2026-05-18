from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, BaseModelMixin


class MonthlyMetric(Base, BaseModelMixin):
    __tablename__ = "monthly_metrics"
    __table_args__ = (
        UniqueConstraint("monitoring_task_id", "date", name="uq_monthly_metric_task_date"),
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
    success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    
    total_downtime_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_uptime_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    incident_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    avg_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)

    achieved_target: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sla_month: Mapped[float | None] = mapped_column(Float, nullable=True)

    monitoring_task = relationship("MonitoringTask", back_populates="monthly_metrics")
