"""Shared fetch-and-validate helpers used by several task use cases."""

from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from use_cases.exceptions import ProjectNotFound, TaskNotFound


async def get_task_or_404(tasks: TodoRepository, user_id: int, task_id: int) -> Todo:
    task = await tasks.get_for_user(user_id, task_id)
    if task is None:
        raise TaskNotFound()
    return task


async def ensure_project(
    tasks: TodoRepository, user_id: int, project_id: int | None
) -> None:
    if (
        project_id is not None
        and await tasks.get_project_for_user(user_id, project_id) is None
    ):
        raise ProjectNotFound()
