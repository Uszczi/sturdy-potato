"""Shared fetch-and-validate helpers used by several task use cases."""

from use_cases.entities import Task
from use_cases.exceptions import ProjectNotFound, TaskNotFound
from use_cases.ports import ProjectRepository, TaskRepository


async def get_task_or_404(
    tasks: TaskRepository, workspace_id: int, task_id: int
) -> Task:
    task = await tasks.get(workspace_id, task_id)
    if task is None:
        raise TaskNotFound()
    return task


async def ensure_project(
    projects: ProjectRepository, workspace_id: int, project_id: int | None
) -> None:
    if project_id is not None and not await projects.exists(workspace_id, project_id):
        raise ProjectNotFound()
