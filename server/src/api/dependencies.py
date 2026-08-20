from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends

from auth import CurrentUser, CurrentUserId
from infrastructure.db import SessionDep
from infrastructure.repositories import UserRepository
from infrastructure.security import password_hasher, token_service
from infrastructure.unit_of_work import UnitOfWork
from use_cases import auth as auth_use_cases
from use_cases import projects as project_use_cases
from use_cases import tasks as task_use_cases


async def get_unit_of_work(session: SessionDep) -> AsyncGenerator[UnitOfWork]:
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise


UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_unit_of_work)]


def _use_case[T](build: Callable[[UnitOfWork], T]) -> Callable[..., T]:
    """Turn a "build from the unit of work" function into a FastAPI provider.

    Each use case names the repositories it needs in ``build``; there is no
    baked-in assumption about how many repositories a use case takes.
    """

    def provider(uow: UnitOfWorkDep) -> T:
        return build(uow)

    return provider


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def provide_authenticate_user(
    users: UserRepositoryDep,
) -> auth_use_cases.AuthenticateUser:
    return auth_use_cases.AuthenticateUser(users, password_hasher, token_service)


def provide_refresh_access_token(
    users: UserRepositoryDep,
) -> auth_use_cases.RefreshAccessToken:
    return auth_use_cases.RefreshAccessToken(users, token_service)


AuthenticateUserDep = Annotated[
    auth_use_cases.AuthenticateUser, Depends(provide_authenticate_user)
]
RefreshAccessTokenDep = Annotated[
    auth_use_cases.RefreshAccessToken, Depends(provide_refresh_access_token)
]
RegisterUserDep = Annotated[
    auth_use_cases.RegisterUser,
    Depends(
        _use_case(
            lambda uow: auth_use_cases.RegisterUser(
                uow.users, password_hasher, token_service
            )
        )
    ),
]

ListTasksDep = Annotated[
    task_use_cases.ListTasks,
    Depends(_use_case(lambda uow: task_use_cases.ListTasks(uow.tasks))),
]
ViewTasksDep = Annotated[
    task_use_cases.ViewTasks,
    Depends(_use_case(lambda uow: task_use_cases.ViewTasks(uow.tasks, uow.projects))),
]
ListOpenTasksDep = Annotated[
    task_use_cases.ListOpenTasks,
    Depends(_use_case(lambda uow: task_use_cases.ListOpenTasks(uow.tasks))),
]
CountTasksDep = Annotated[
    task_use_cases.CountTasks,
    Depends(_use_case(lambda uow: task_use_cases.CountTasks(uow.tasks))),
]
CreateTaskDep = Annotated[
    task_use_cases.CreateTask,
    Depends(_use_case(lambda uow: task_use_cases.CreateTask(uow.tasks, uow.projects))),
]
GetTaskDep = Annotated[
    task_use_cases.GetTask,
    Depends(_use_case(lambda uow: task_use_cases.GetTask(uow.tasks))),
]
UpdateTaskDep = Annotated[
    task_use_cases.UpdateTask,
    Depends(_use_case(lambda uow: task_use_cases.UpdateTask(uow.tasks, uow.projects))),
]
DeleteTaskDep = Annotated[
    task_use_cases.DeleteTask,
    Depends(_use_case(lambda uow: task_use_cases.DeleteTask(uow.tasks))),
]
ReorderTasksDep = Annotated[
    task_use_cases.ReorderTasks,
    Depends(_use_case(lambda uow: task_use_cases.ReorderTasks(uow.tasks))),
]

ListProjectsDep = Annotated[
    project_use_cases.ListProjects,
    Depends(_use_case(lambda uow: project_use_cases.ListProjects(uow.projects))),
]
CreateProjectDep = Annotated[
    project_use_cases.CreateProject,
    Depends(_use_case(lambda uow: project_use_cases.CreateProject(uow.projects))),
]
GetProjectDep = Annotated[
    project_use_cases.GetProject,
    Depends(_use_case(lambda uow: project_use_cases.GetProject(uow.projects))),
]
UpdateProjectDep = Annotated[
    project_use_cases.UpdateProject,
    Depends(_use_case(lambda uow: project_use_cases.UpdateProject(uow.projects))),
]
DeleteProjectDep = Annotated[
    project_use_cases.DeleteProject,
    Depends(_use_case(lambda uow: project_use_cases.DeleteProject(uow.projects))),
]
ReorderProjectsDep = Annotated[
    project_use_cases.ReorderProjects,
    Depends(_use_case(lambda uow: project_use_cases.ReorderProjects(uow.projects))),
]

__all__ = [
    "AuthenticateUserDep",
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
    "RefreshAccessTokenDep",
    "RegisterUserDep",
    "ReorderProjectsDep",
    "ReorderTasksDep",
    "SessionDep",
    "UnitOfWorkDep",
    "UpdateProjectDep",
    "UpdateTaskDep",
    "UserRepositoryDep",
    "ViewTasksDep",
]
