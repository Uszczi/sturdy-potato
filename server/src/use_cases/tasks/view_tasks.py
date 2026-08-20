from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from use_cases.entities import Task
from use_cases.exceptions import InvalidTimezone
from use_cases.ports import ProjectRepository, TaskRepository
from use_cases.tasks._helpers import ensure_project


def _today_in(tz: str) -> date:
    # "Today" is a calendar date in the caller's zone, so a user in UTC+13 and
    # one in UTC-11 can legitimately disagree on which day it is.
    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError):
        raise InvalidTimezone() from None
    return datetime.now(zone).date()


class ViewTasks:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository) -> None:
        self._tasks = tasks
        self._projects = projects

    async def execute(
        self, user_id: int, *, view: str, project_id: int | None, tz: str = "UTC"
    ) -> list[Task]:
        await ensure_project(self._projects, user_id, project_id)
        today = _today_in(tz)
        return await self._tasks.list_for_view(
            user_id, view=view, project_id=project_id, today=today
        )
