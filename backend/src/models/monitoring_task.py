from sqlalchemy.orm import Mapped

from src.models.base import Base, BaseModelMixin


class MonitoringTask(Base, BaseModelMixin):
    __tablename__ = "monitoring_tasks"

    name: Mapped[str]
