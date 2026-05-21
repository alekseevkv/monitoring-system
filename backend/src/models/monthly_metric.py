from datetime import date

from sqlalchemy import Boolean, Computed, Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, BaseModelMixin


class MonthlyMetric(Base, BaseModelMixin):
    __tablename__ = "monthly_metrics"
    __table_args__ = (
        UniqueConstraint("monitoring_task_id", "metric_date", name="uq_monthly_metric_task_date"),
    )

    monitoring_task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)

    successful_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_checks: Mapped[int] = mapped_column(
        Integer,
        Computed("successful_checks + failed_checks", persisted=True),
        nullable=False,
    )
    success_rate: Mapped[float] = mapped_column(
        Float,
        Computed(
            "CASE WHEN successful_checks + failed_checks = 0 THEN 100.0 "
            "ELSE successful_checks * 100.0 / (successful_checks + failed_checks) END",
            persisted=True,
        ),
        nullable=False,
    )

    total_downtime_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_uptime_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    incident_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sla_month: Mapped[float | None] = mapped_column(
        Float,
        Computed(
            "CASE WHEN total_uptime_seconds IS NULL OR total_downtime_seconds IS NULL THEN NULL "
            "WHEN total_uptime_seconds + total_downtime_seconds = 0 THEN 100.0 "
            "ELSE total_uptime_seconds * 100.0 / (total_uptime_seconds + total_downtime_seconds) END",
            persisted=True,
        ),
        nullable=True,
    )

    avg_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_response_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)

    achieved_target: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    monitoring_task = relationship("MonitoringTask", back_populates="monthly_metrics")
