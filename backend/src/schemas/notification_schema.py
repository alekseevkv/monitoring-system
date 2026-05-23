from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TriggerType = Literal["down", "up", "reminder"]
NotificationStatus = Literal["pending", "sent", "failed"]


class NotificationResponse(BaseModel):
    id: int
    incident_id: int
    recipient_email: str
    trigger_type: TriggerType
    subject: str
    body: str
    status: NotificationStatus
    error_message: str | None
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
