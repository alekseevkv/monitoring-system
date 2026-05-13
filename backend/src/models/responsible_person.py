from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, BaseModelMixin


class ResponsiblePerson(Base, BaseModelMixin):
    __tablename__ = "responsible_persons"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    monitoring_task_id: Mapped[int] = mapped_column(ForeignKey("monitoring_tasks.id"))
    monitoring_task: Mapped["MonitoringTask"] = relationship(  # type: ignore # noqa: F821
        "MonitoringTask", back_populates="responsible_persons"
    )
