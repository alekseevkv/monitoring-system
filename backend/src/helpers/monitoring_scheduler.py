"""
Планировщик мониторинга c двумя режимами:
- cron_expression (5 или 6 полей)
- check_interval_seconds
При старте приложения загружает все активные задачи из БД и регистрирует джобы
При добавлении/удалении задач обновляется
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.database import async_session_maker
from src.models.monitoring_task import MonitoringTask
from src.repositories.monitoring_task import MonitoringTaskRepository
from src.repositories.check_result import CheckResultRepository
from src.repositories.incidents import IncidentRepository
from src.services.check_result_service import CheckResultService
from src.services.incident_service import IncidentService
from src.services.monitoring_task_service import MonitoringTaskService
from src.helpers.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

class MonitoringScheduler:
    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self._scheduler.start()

    def shutdown(self) -> None:
        self._scheduler.shutdown(wait=False)

    def schedule_task(self, task: MonitoringTask) -> None:
        """Добавляет или заменяет джоб"""
        # Планируем задачу мониторинга (cron или interval)
        try:
            trigger = _make_trigger(task)
        except ValueError as exc:
            logger.error(f"Can't schedule task {task.id}: {exc}")
            return

        self._scheduler.add_job(
            _run_task_check,
            trigger=trigger,
            args=[task.id],
            id=f"task_{task.id}",
            name=task.name,
            replace_existing=True,
            misfire_grace_time=10,
        )
        logger.info(f"Scheduled task '{task.name}' id={task.id}, trigger={trigger}")

    def unschedule_task(self, task_id: int) -> None:
        """Удаляет джоб (если существует)"""
        job = self._scheduler.get_job(f"task_{task_id}")
        if job:
            job.remove()
            logger.info(f"Unscheduled task id={task_id}")

    async def load_from_db(self) -> None:
        """Загружает активные задачи из БД и регистрирует джобы"""
        async with async_session_maker() as session:
            repo = MonitoringTaskRepository(session)
            tasks = await repo.get_active()
            for task in tasks:
                self.schedule_task(task)

monitoring_scheduler = MonitoringScheduler()

def _make_trigger(task: MonitoringTask) -> IntervalTrigger | CronTrigger:
    """Определяет тип триггера: cron или interval"""
    if task.cron_expression:
        parts = task.cron_expression.strip().split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
            second = "0"
        elif len(parts) == 6:
            second, minute, hour, day, month, day_of_week = parts
        else:
            raise ValueError(
                f"Invalid cron expression '{task.cron_expression}': expected 5 or 6 fields"
            )
        return CronTrigger(
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
        )
    return IntervalTrigger(seconds=task.check_interval_seconds)

async def _run_task_check(task_id: int) -> None:
    """Запуск проверки, вызывается при срабатывании триггера"""
    async with async_session_maker() as session:
        task = await session.get(MonitoringTask, task_id)
        if task is None or not task.is_active:
            logger.info(f"Task {task_id} not found or inactive —> skip")
            return
        try:
            orchestrator = _build_orchestrator(session)
            await orchestrator.run_check(task)
        except Exception:
            logger.exception(f"Error while checking task {task_id}")

def _build_orchestrator(session) -> Orchestrator:
    check_service = CheckResultService(CheckResultRepository(session))
    incident_service = IncidentService(IncidentRepository(session))
    task_service = MonitoringTaskService(MonitoringTaskRepository(session))
    return Orchestrator(check_service, incident_service, task_service)