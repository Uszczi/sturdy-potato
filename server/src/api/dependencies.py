"""Central definitions for the FastAPI dependencies used across the API."""

from typing import Annotated

from fastapi import Depends

from auth import CurrentUser, CurrentUserId
from infrastructure.db import SessionDep
from infrastructure.repositories import (
    ProjectRepository,
    TodoRepository,
    UserRepository,
)


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_todo_repository(session: SessionDep) -> TodoRepository:
    return TodoRepository(session)


def get_project_repository(session: SessionDep) -> ProjectRepository:
    return ProjectRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
TodoRepositoryDep = Annotated[TodoRepository, Depends(get_todo_repository)]
ProjectRepositoryDep = Annotated[ProjectRepository, Depends(get_project_repository)]

__all__ = [
    "CurrentUser",
    "CurrentUserId",
    "ProjectRepositoryDep",
    "SessionDep",
    "TodoRepositoryDep",
    "UserRepositoryDep",
]
