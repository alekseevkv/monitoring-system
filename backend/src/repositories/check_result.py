from typing import Sequence
from datetime import datetime

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.check_result import CheckResult


class CheckResultRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> CheckResult:
        result = CheckResult(**data)
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def update(self, check_id: int, data: dict) -> CheckResult | None:
        check = await self.get_by_id(check_id)
        if not check:
            return None
        for key, value in data.items():
            setattr(check, key, value)
        await self.db.commit()
        await self.db.refresh(check)
        return check

    async def get_by_id(self, result_id: int) -> CheckResult | None:
        stmt = select(CheckResult).where(CheckResult.id == result_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_task_id(
        self, task_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[Sequence[CheckResult], int]:
        total = (
            await self.db.execute(
                select(func.count())
                .select_from(CheckResult)
                .where(CheckResult.monitoring_task_id == task_id)
            )
        ).scalar_one()

        rows = list(
            (
                await self.db.execute(
                    select(CheckResult)
                    .where(CheckResult.monitoring_task_id == task_id)
                    .order_by(CheckResult.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                )
            ).scalars().all()
        )
        return rows, total

    async def get_stats_for_period(
        self, task_id: int, start: datetime, end: datetime
    ) -> dict:
        row = (
            await self.db.execute(
                select(
                    func.count(CheckResult.id).label("total"),
                    func.count(CheckResult.id)
                    .filter(CheckResult.is_success == True)  # noqa: E712
                    .label("successful"),
                    func.avg(CheckResult.response_time_s).label("avg_response_time"),
                    func.min(CheckResult.response_time_s).label("min_response_time"),
                    func.max(CheckResult.response_time_s).label("max_response_time"),
                ).where(
                    and_(
                        CheckResult.monitoring_task_id == task_id,
                        CheckResult.created_at >= start,
                        CheckResult.created_at <= end,
                    )
                )
            )
        ).one()
        return {
            "total": row.total or 0,
            "successful": row.successful or 0,
            "avg_response_time": float(row.avg_response_time) if row.avg_response_time else None,
            "min_response_time": float(row.min_response_time) if row.min_response_time else None,
            "max_response_time": float(row.max_response_time) if row.max_response_time else None,
        }

    async def get_first_check_time(self, task_id: int) -> datetime | None:
        stmt = (
            select(CheckResult.created_at)
            .where(CheckResult.monitoring_task_id == task_id)
            .order_by(CheckResult.created_at.asc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_latest_by_task(self, task_id: int) -> CheckResult | None:
        stmt = (
            select(CheckResult)
            .where(CheckResult.monitoring_task_id == task_id)
            .order_by(CheckResult.created_at.desc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()


async def get_check_result_repository(
    db: AsyncSession = Depends(get_session),
) -> CheckResultRepository:
    return CheckResultRepository(db)
