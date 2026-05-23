from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TriggerType = Literal["down", "up", "reminder"]
NotificationStatus = Literal["pending", "sent", "failed"]


class NotificationResponse(BaseModel):
    id: int
    monitoring_task_id: int
    recipient_email: str
    trigger_type: TriggerType
    subject: str
    body: str
    status: NotificationStatus
    error_message: str | None
    sent_at: datetime | None
    archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
