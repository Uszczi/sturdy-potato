from typing import Any

from rest_framework.exceptions import NotFound

from infrastructure.models import Project, Todo, User
from infrastructure.repositories import ProjectRepository, TodoRepository
from serializers.project.project import ProjectSchema
from serializers.todo.task import TodoSchema


async def get_task_or_404(
    repository: TodoRepository,
    user: User,
    task_id: int,
) -> Todo:
    task = await repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")
    return task


async def get_project_or_404(
    repository: ProjectRepository,
    user: User,
    project_id: int,
) -> Project:
    project = await repository.get_for_user(user, project_id)
    if project is None:
        raise NotFound("Project not found.")
    return project


def dump_task(task: Todo) -> dict[str, Any]:
    return TodoSchema.model_validate(task).model_dump(mode="json")


def dump_project(project: Project) -> dict[str, Any]:
    return ProjectSchema.model_validate(project).model_dump(mode="json")


async def resolve_project(
    repository: ProjectRepository,
    user: User,
    data: dict[str, Any],
) -> dict[str, Any]:
    if "project_id" not in data:
        return data

    project_id = data.pop("project_id")
    data["project"] = (
        None
        if project_id is None
        else await get_project_or_404(repository, user, project_id)
    )
    return data
