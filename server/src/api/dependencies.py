"""Central definitions for the FastAPI dependencies used across the API.

This module is the composition root: it wires repositories to a session and use
cases to their repositories. Use cases stay framework-agnostic; the ``Depends``
plumbing lives here.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from auth import CurrentUser, CurrentUserId
from infrastructure.db import SessionDep
from infrastructure.repositories import (
    ProjectRepository,
    TodoRepository,
    UserRepository,
)
from use_cases import projects as project_use_cases
from use_cases import tasks as task_use_cases


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_todo_repository(session: SessionDep) -> TodoRepository:
    return TodoRepository(session)


def get_project_repository(session: SessionDep) -> ProjectRepository:
    return ProjectRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
TodoRepositoryDep = Annotated[TodoRepository, Depends(get_todo_repository)]
ProjectRepositoryDep = Annotated[ProjectRepository, Depends(get_project_repository)]


def _task_use_case[T](cls: Callable[[TodoRepository], T]) -> Callable[..., T]:
    def provider(tasks: TodoRepositoryDep) -> T:
        return cls(tasks)

    return provider


def _project_use_case[T](cls: Callable[[ProjectRepository], T]) -> Callable[..., T]:
    def provider(projects: ProjectRepositoryDep) -> T:
        return cls(projects)

    return provider


ListTasksDep = Annotated[
    task_use_cases.ListTasks, Depends(_task_use_case(task_use_cases.ListTasks))
]
ViewTasksDep = Annotated[
    task_use_cases.ViewTasks, Depends(_task_use_case(task_use_cases.ViewTasks))
]
ListOpenTasksDep = Annotated[
    task_use_cases.ListOpenTasks, Depends(_task_use_case(task_use_cases.ListOpenTasks))
]
CountTasksDep = Annotated[
    task_use_cases.CountTasks, Depends(_task_use_case(task_use_cases.CountTasks))
]
CreateTaskDep = Annotated[
    task_use_cases.CreateTask, Depends(_task_use_case(task_use_cases.CreateTask))
]
GetTaskDep = Annotated[
    task_use_cases.GetTask, Depends(_task_use_case(task_use_cases.GetTask))
]
UpdateTaskDep = Annotated[
    task_use_cases.UpdateTask, Depends(_task_use_case(task_use_cases.UpdateTask))
]
DeleteTaskDep = Annotated[
    task_use_cases.DeleteTask, Depends(_task_use_case(task_use_cases.DeleteTask))
]
ReorderTasksDep = Annotated[
    task_use_cases.ReorderTasks, Depends(_task_use_case(task_use_cases.ReorderTasks))
]

ListProjectsDep = Annotated[
    project_use_cases.ListProjects,
    Depends(_project_use_case(project_use_cases.ListProjects)),
]
CreateProjectDep = Annotated[
    project_use_cases.CreateProject,
    Depends(_project_use_case(project_use_cases.CreateProject)),
]
GetProjectDep = Annotated[
    project_use_cases.GetProject,
    Depends(_project_use_case(project_use_cases.GetProject)),
]
UpdateProjectDep = Annotated[
    project_use_cases.UpdateProject,
    Depends(_project_use_case(project_use_cases.UpdateProject)),
]
DeleteProjectDep = Annotated[
    project_use_cases.DeleteProject,
    Depends(_project_use_case(project_use_cases.DeleteProject)),
]
ReorderProjectsDep = Annotated[
    project_use_cases.ReorderProjects,
    Depends(_project_use_case(project_use_cases.ReorderProjects)),
]

__all__ = [
    "CountTasksDep",
    "CreateProjectDep",
    "CreateTaskDep",
    "CurrentUser",
    "CurrentUserId",
    "DeleteProjectDep",
    "DeleteTaskDep",
    "GetProjectDep",
    "GetTaskDep",
    "ListOpenTasksDep",
    "ListProjectsDep",
    "ListTasksDep",
    "ProjectRepositoryDep",
    "ReorderProjectsDep",
    "ReorderTasksDep",
    "SessionDep",
    "TodoRepositoryDep",
    "UpdateProjectDep",
    "UpdateTaskDep",
    "UserRepositoryDep",
    "ViewTasksDep",
]
