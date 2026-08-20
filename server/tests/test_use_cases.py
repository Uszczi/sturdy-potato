"""Use-case unit tests: no FastAPI, no database, just ports and fakes.

If these ever need a real session or an HTTP client to run, the use-case layer
has stopped being framework-agnostic — which is exactly what this suite guards.
"""

from datetime import UTC, datetime

import pytest

from tests.fakes import (
    FakePasswordHasher,
    FakeProjectRepository,
    FakeTaskRepository,
    FakeTokenIssuer,
    FakeUserRepository,
)
from use_cases.auth.authenticate_user import AuthenticateUser
from use_cases.auth.get_current_user import GetCurrentUser
from use_cases.auth.refresh_access_token import RefreshAccessToken
from use_cases.dtos import (
    ProjectCreateData,
    TaskCreateData,
    TaskUpdateData,
)
from use_cases.entities import Project, Task, User
from use_cases.exceptions import (
    InvalidCredentials,
    InvalidReorder,
    InvalidToken,
    ProjectNameConflict,
    ProjectNotFound,
    TaskNotFound,
)
from use_cases.projects.create_project import CreateProject
from use_cases.tasks.create_task import CreateTask
from use_cases.tasks.delete_task import DeleteTask
from use_cases.tasks.reorder_tasks import ReorderTasks
from use_cases.tasks.update_task import UpdateTask

USER = 1


def _user(*, is_active: bool = True) -> User:
    return User(
        id=USER,
        username="demo",
        hashed_password=FakePasswordHasher().hash("secret"),
        is_active=is_active,
        is_staff=False,
    )


def _authenticate(user: User | None) -> AuthenticateUser:
    users = FakeUserRepository([user] if user is not None else [])
    return AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer())


def _task(task_id: int, *, position: int, project_id: int | None = None) -> Task:
    now = datetime(2024, 1, 1, tzinfo=UTC)
    return Task(
        id=task_id,
        user_id=USER,
        project_id=project_id,
        title=f"Task {task_id}",
        description="",
        completed=False,
        position=position,
        due_date=None,
        created_at=now,
        updated_at=now,
    )


def _project(project_id: int, *, name: str = "Work") -> Project:
    now = datetime(2024, 1, 1, tzinfo=UTC)
    return Project(
        id=project_id,
        user_id=USER,
        name=name,
        color=None,
        position=0,
        task_count=0,
        created_at=now,
        updated_at=now,
    )


def _create_data(*, project_id: int | None = None) -> TaskCreateData:
    return TaskCreateData(
        title="Write tests",
        description="",
        completed=False,
        project_id=project_id,
        due_date=None,
    )


async def test_create_task_rejects_project_owned_by_nobody() -> None:
    tasks = FakeTaskRepository()
    projects = FakeProjectRepository()  # no projects exist

    with pytest.raises(ProjectNotFound):
        await CreateTask(tasks, projects).execute(USER, _create_data(project_id=99))


async def test_create_task_accepts_an_owned_project() -> None:
    tasks = FakeTaskRepository()
    projects = FakeProjectRepository([_project(5)])

    task = await CreateTask(tasks, projects).execute(USER, _create_data(project_id=5))

    assert task.project_id == 5
    assert task.id is not None


async def test_update_task_only_touches_provided_fields() -> None:
    tasks = FakeTaskRepository([_task(1, position=0)])
    projects = FakeProjectRepository()

    updated = await UpdateTask(tasks, projects).execute(
        USER, 1, TaskUpdateData(completed=True)
    )

    # exclude_unset: title left alone, only completed changed.
    assert updated.completed is True
    assert updated.title == "Task 1"


async def test_update_task_missing_raises_not_found() -> None:
    tasks = FakeTaskRepository()
    projects = FakeProjectRepository()

    with pytest.raises(TaskNotFound):
        await UpdateTask(tasks, projects).execute(USER, 1, TaskUpdateData(title="x"))


async def test_delete_task_missing_raises_not_found() -> None:
    with pytest.raises(TaskNotFound):
        await DeleteTask(FakeTaskRepository()).execute(USER, 1)


async def test_reorder_rejects_ids_outside_the_user() -> None:
    tasks = FakeTaskRepository([_task(1, position=0), _task(2, position=1)])

    with pytest.raises(InvalidReorder):
        await ReorderTasks(tasks).execute(USER, [1, 999])


async def test_reorder_swaps_positions_of_the_subset() -> None:
    tasks = FakeTaskRepository(
        [_task(1, position=0), _task(2, position=1), _task(3, position=2)]
    )

    # Move task 3 ahead of task 1 within the slots they occupy.
    await ReorderTasks(tasks).execute(USER, [3, 1])

    assert await tasks.ordered_ids(USER) == [3, 2, 1]


async def test_create_project_rejects_duplicate_name() -> None:
    projects = FakeProjectRepository([_project(1, name="Work")])

    with pytest.raises(ProjectNameConflict):
        await CreateProject(projects).execute(USER, ProjectCreateData("Work", None))


async def test_authenticate_issues_a_token_pair_for_valid_credentials() -> None:
    tokens = await _authenticate(_user()).execute("demo", "secret")

    assert tokens.access == f"access:{USER}"
    assert tokens.refresh == f"refresh:{USER}"


async def test_authenticate_rejects_a_wrong_password() -> None:
    with pytest.raises(InvalidCredentials):
        await _authenticate(_user()).execute("demo", "wrong")


async def test_authenticate_rejects_an_unknown_user() -> None:
    with pytest.raises(InvalidCredentials):
        await _authenticate(None).execute("ghost", "secret")


async def test_authenticate_rejects_an_inactive_user() -> None:
    with pytest.raises(InvalidCredentials):
        await _authenticate(_user(is_active=False)).execute("demo", "secret")


def _refresh(user: User | None) -> RefreshAccessToken:
    users = FakeUserRepository([user] if user is not None else [])
    return RefreshAccessToken(users, FakeTokenIssuer())


async def test_refresh_returns_a_new_access_token() -> None:
    use_case = _refresh(_user())

    assert await use_case.execute(f"refresh:{USER}") == f"access:{USER}"


async def test_refresh_rejects_a_non_refresh_token() -> None:
    with pytest.raises(InvalidToken):
        await _refresh(_user()).execute(f"access:{USER}")


async def test_refresh_rejects_a_missing_user() -> None:
    # A refresh token that decodes fine but whose account no longer exists must
    # not keep minting access tokens.
    with pytest.raises(InvalidToken):
        await _refresh(None).execute(f"refresh:{USER}")


async def test_refresh_rejects_an_inactive_user() -> None:
    with pytest.raises(InvalidToken):
        await _refresh(_user(is_active=False)).execute(f"refresh:{USER}")


def _get_current_user(user: User | None) -> GetCurrentUser:
    users = FakeUserRepository([user] if user is not None else [])
    return GetCurrentUser(users, FakeTokenIssuer())


async def test_get_current_user_resolves_a_valid_access_token() -> None:
    resolved = await _get_current_user(_user()).execute("access:1")

    assert resolved.id == USER


async def test_get_current_user_rejects_a_non_access_token() -> None:
    with pytest.raises(InvalidToken):
        await _get_current_user(_user()).execute("refresh:1")


async def test_get_current_user_rejects_a_missing_user() -> None:
    with pytest.raises(InvalidToken):
        await _get_current_user(None).execute("access:1")


async def test_get_current_user_rejects_an_inactive_user() -> None:
    with pytest.raises(InvalidToken):
        await _get_current_user(_user(is_active=False)).execute("access:1")
