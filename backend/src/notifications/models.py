from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, BaseModelMixin


class Notification(Base, BaseModelMixin):
    __tablename__ = "notifications"

    monitoring_task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE")
    )
    recipient_email: Mapped[str] = mapped_column(String(255))
    trigger_type: Mapped[str] = mapped_column(String(50))  # down / up / reminder
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending / sent / failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
