from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.archived == False)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, notification_id: int) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_monitoring_task(
        self, monitoring_task_id: int, skip: int = 0, limit: int = 100
    ) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(
                and_(
                    Notification.monitoring_task_id == monitoring_task_id,
                    Notification.archived == False,
                )
            )
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_last_sent_for_monitoring_task(self, monitoring_task_id: int) -> Notification | None:
        """Returns the most recent successfully sent notification for throttle checks."""
        result = await self.session.execute(
            select(Notification)
            .where(
                and_(
                    Notification.monitoring_task_id == monitoring_task_id,
                    Notification.status == "sent",
                    Notification.archived == False,
                )
            )
            .order_by(Notification.sent_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Notification:
        notification = Notification(**data)
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def update(self, notification: Notification, data: dict) -> Notification:
        for key, value in data.items():
            setattr(notification, key, value)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification
