from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
 
import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
 
from src.helpers import monitoring_scheduler as sched
from src.helpers.monitoring_scheduler import (
    MonitoringScheduler,
    _make_trigger,
    _run_task_check,
)
 
from tests.helpers import make_session_maker, real_task_row

def _cron_fields(trigger: CronTrigger) -> dict[str, str]: # {field_name: value}
    return {f.name: str(f) for f in trigger.fields}

@pytest.fixture
def load_env(scheduler):
    session = MagicMock()
    repo = MagicMock()
    repo.get_active = AsyncMock(return_value=[])

    with (
        patch.object(scheduler, "schedule_task") as schedule_spy,
        patch(
            "src.helpers.monitoring_scheduler.async_session_maker",
            make_session_maker(session),
        ),
        patch(
            "src.helpers.monitoring_scheduler.MonitoringTaskRepository",
            return_value=repo,
        ),
    ):
        yield SimpleNamespace(repo=repo, session=session, schedule_spy=schedule_spy)

@pytest.fixture
def check_env():
    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    orchestrator = MagicMock()
    orchestrator.run_check = AsyncMock()

    with (
        patch(
            "src.helpers.monitoring_scheduler.async_session_maker",
            make_session_maker(session),
        ),
        patch(
            "src.helpers.monitoring_scheduler._build_orchestrator",
            return_value=orchestrator,
        ) as build,
    ):
        yield SimpleNamespace(
            session=session,
            orchestrator=orchestrator,
            build=build,
        )

class TestMakeTrigger:
    def test_interval_trigger(self):
        task = real_task_row(cron_expression=None, check_interval_seconds=120)
        trigger = _make_trigger(task)
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.total_seconds() == 120
 
    def test_empty_cron_string(self):
        task = real_task_row(cron_expression="", check_interval_seconds=120)
        trigger = _make_trigger(task)
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.total_seconds() == 120
 
    def test_five_field_cron_trigger(self):
        task = real_task_row(cron_expression="*/1 2 3 4 5")
        trigger = _make_trigger(task)
        assert isinstance(trigger, CronTrigger)
        fields = _cron_fields(trigger)
        assert fields["minute"] == "*/1"
        assert fields["hour"] == "2"
        assert fields["day"] == "3"
        assert fields["month"] == "4"
        assert fields["day_of_week"] == "5"
        assert fields["second"] == "0"
 
    def test_six_field_cron_trigger(self):
        task = real_task_row(cron_expression="30 15 10 2 6 3")
        trigger = _make_trigger(task)
        assert isinstance(trigger, CronTrigger)
        fields = _cron_fields(trigger)
        assert fields["second"] == "30"
        assert fields["minute"] == "15"
        assert fields["hour"] == "10"
        assert fields["day"] == "2"
        assert fields["month"] == "6"
        assert fields["day_of_week"] == "3"
 
    def test_whitespace_is_stripped(self):
        task = real_task_row(cron_expression="  */10 * * * *  ")
        trigger = _make_trigger(task)
        assert isinstance(trigger, CronTrigger)
        assert _cron_fields(trigger)["minute"] == "*/10"
 
    @pytest.mark.parametrize("cron_expression", ["* * * *", "* * * * * * *", "*"])
    def test_invalid_cron_raises_value_error(self, cron_expression):
        task = real_task_row(cron_expression=cron_expression)
        with pytest.raises(ValueError, match=r"expected 5 or 6 fields$"):
            _make_trigger(task)
 
 
class TestMonitoringScheduler:
    @pytest.fixture
    def scheduler(self):
        scheduler = MonitoringScheduler()
        scheduler._scheduler = MagicMock() # мок AsyncIOScheduler
        return scheduler
 
    def test_start_success(self, scheduler):
        scheduler.start()
        scheduler._scheduler.start.assert_called_once_with()
 
    def test_shutdown_success(self, scheduler):
        scheduler.shutdown()
        scheduler._scheduler.shutdown.assert_called_once_with(wait=False)
 
    def test_schedule_with_interval(self, scheduler):
        task = real_task_row(id=1, name="API", check_interval_seconds=60)
        scheduler.schedule_task(task)
 
        scheduler._scheduler.add_job.assert_called_once()
        call = scheduler._scheduler.add_job.call_args
        assert call.args[0] is sched._run_task_check
        kwargs = call.kwargs
        assert isinstance(kwargs["trigger"], IntervalTrigger)
        assert kwargs["args"] == [1]
        assert kwargs["id"] == "task_1"
        assert kwargs["name"] == "API"
        assert kwargs["replace_existing"] is True
        assert kwargs["misfire_grace_time"] == 10
 
    def test_schedule_with_valid_cron(self, scheduler):
        task = real_task_row(id=1, cron_expression="0 0 * * *")
        scheduler.schedule_task(task)
        trigger = scheduler._scheduler.add_job.call_args.kwargs["trigger"]
        assert isinstance(trigger, CronTrigger)
 
    def test_schedule_with_invalid_cron(self, scheduler):
        task = real_task_row(id=9, cron_expression="invalid cron expression")
        scheduler.schedule_task(task)
        scheduler._scheduler.add_job.assert_not_called()
 
    def test_unschedule_existing_job(self, scheduler):
        job = MagicMock()
        scheduler._scheduler.get_job.return_value = job
        scheduler.unschedule_task(1)
        scheduler._scheduler.get_job.assert_called_once_with("task_1")
        job.remove.assert_called_once_with()
 
    def test_unschedule_non_existing_job(self, scheduler):
        scheduler._scheduler.get_job.return_value = None
        scheduler.unschedule_task(999)
        scheduler._scheduler.get_job.assert_called_once_with("task_999")
 
    async def test_load_active_tasks_from_db(self, scheduler, load_env):
        tasks = [real_task_row(id=1), real_task_row(id=2), real_task_row(id=3)]
        load_env.repo.get_active = AsyncMock(return_value=tasks)

        await scheduler.load_from_db()

        load_env.repo.get_active.assert_awaited_once_with()
        assert load_env.schedule_spy.call_count == 3
        scheduled = [c.args[0] for c in load_env.schedule_spy.call_args_list]
        assert scheduled == tasks

    async def test_load_no_tasks_from_db(self, scheduler, load_env):
        load_env.repo.get_active = AsyncMock(return_value=[])

        await scheduler.load_from_db()

        load_env.schedule_spy.assert_not_called()
 

class TestRunTaskCheck:
    async def test_run_check_for_active_task(self, check_env):
        task = real_task_row(id=5, is_active=True)
        check_env.session.get = AsyncMock(return_value=task)

        await _run_task_check(5)

        check_env.build.assert_called_once_with(check_env.session)
        check_env.orchestrator.run_check.assert_awaited_once_with(task)

    async def test_skip_for_missing_task(self, check_env):
        check_env.session.get = AsyncMock(return_value=None)

        await _run_task_check(5)

        check_env.build.assert_not_called()

    async def test_skip_for_inactive_task(self, check_env):
        task = real_task_row(id=5, is_active=False)
        check_env.session.get = AsyncMock(return_value=task)

        await _run_task_check(5)

        check_env.build.assert_not_called()

    async def test_orchestrator_exception(self, check_env):
        task = real_task_row(id=5, is_active=True)
        check_env.session.get = AsyncMock(return_value=task)
        check_env.orchestrator.run_check = AsyncMock(side_effect=RuntimeError("error"))

        await _run_task_check(5)

        check_env.orchestrator.run_check.assert_awaited_once_with(task)