"""Use-case unit tests: no FastAPI, no database, just ports and fakes.

If these ever need a real session or an HTTP client to run, the use-case layer
has stopped being framework-agnostic — which is exactly what this suite guards.
"""

from datetime import UTC, datetime

import pytest

from tests.fakes import (
    FakeCommentRepository,
    FakePasswordHasher,
    FakeProjectRepository,
    FakeTaskRepository,
    FakeTokenIssuer,
    FakeUserRepository,
)
from use_cases.auth.authenticate_user import AuthenticateUser
from use_cases.auth.get_current_user import GetCurrentUser
from use_cases.auth.refresh_access_token import RefreshAccessToken
from use_cases.auth.register_user import RegisterUser
from use_cases.comments.create_comment import CreateComment
from use_cases.comments.delete_comment import DeleteComment
from use_cases.comments.list_comments import ListComments
from use_cases.comments.update_comment import UpdateComment
from use_cases.dtos import (
    CommentCreateData,
    CommentUpdateData,
    ProjectCreateData,
    TaskCreateData,
    TaskUpdateData,
)
from use_cases.entities import Comment, Project, Task, User
from use_cases.exceptions import (
    CommentNotFound,
    InvalidCredentials,
    InvalidReorder,
    InvalidToken,
    ProjectNameConflict,
    ProjectNotFound,
    TaskNotFound,
    UseCaseError,
    UsernameConflict,
)
from use_cases.projects.create_project import CreateProject
from use_cases.task_status import TaskStatus
from use_cases.tasks.create_task import CreateTask
from use_cases.tasks.delete_task import DeleteTask
from use_cases.tasks.list_open_tasks import ListOpenTasks
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
        status=TaskStatus.OPEN,
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
        status=TaskStatus.OPEN,
        project_id=project_id,
        due_date=None,
    )


def _comment(comment_id: int, *, task_id: int) -> Comment:
    now = datetime(2024, 1, 1, tzinfo=UTC)
    return Comment(
        id=comment_id,
        task_id=task_id,
        user_id=USER,
        body=f"Comment {comment_id}",
        created_at=now,
        updated_at=now,
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
        USER, 1, TaskUpdateData(status=TaskStatus.DONE)
    )

    # exclude_unset: title left alone, only status changed.
    assert updated.status is TaskStatus.DONE
    assert updated.title == "Task 1"


async def test_update_task_missing_raises_not_found() -> None:
    tasks = FakeTaskRepository()
    projects = FakeProjectRepository()

    with pytest.raises(TaskNotFound):
        await UpdateTask(tasks, projects).execute(USER, 1, TaskUpdateData(title="x"))


async def test_delete_task_missing_raises_not_found() -> None:
    with pytest.raises(TaskNotFound):
        await DeleteTask(FakeTaskRepository()).execute(USER, 1)


async def test_list_open_excludes_done_tasks() -> None:
    done = _task(1, position=0)
    done = Task(**{**done.__dict__, "status": TaskStatus.DONE})
    tasks = FakeTaskRepository([done, _task(2, position=1)])

    listed = await ListOpenTasks(tasks).execute(USER, limit=None)

    # The done task is filtered out; only the still-open one remains.
    assert [t.id for t in listed] == [2]


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


async def test_create_comment_requires_an_existing_task() -> None:
    comments = FakeCommentRepository()
    tasks = FakeTaskRepository()  # no tasks exist

    with pytest.raises(TaskNotFound):
        await CreateComment(comments, tasks).execute(
            USER, 1, CommentCreateData(body="hi")
        )


async def test_create_comment_on_an_owned_task_succeeds() -> None:
    comments = FakeCommentRepository()
    tasks = FakeTaskRepository([_task(1, position=0)])

    comment = await CreateComment(comments, tasks).execute(
        USER, 1, CommentCreateData(body="hi")
    )

    assert comment.task_id == 1
    assert comment.body == "hi"


async def test_list_comments_requires_an_existing_task() -> None:
    comments = FakeCommentRepository([_comment(1, task_id=1)])
    tasks = FakeTaskRepository()

    with pytest.raises(TaskNotFound):
        await ListComments(comments, tasks).execute(USER, 1)


async def test_list_comments_returns_the_tasks_thread() -> None:
    comments = FakeCommentRepository([_comment(1, task_id=1), _comment(2, task_id=2)])
    tasks = FakeTaskRepository([_task(1, position=0)])

    listed = await ListComments(comments, tasks).execute(USER, 1)

    assert [c.id for c in listed] == [1]


async def test_update_comment_changes_the_body() -> None:
    comments = FakeCommentRepository([_comment(1, task_id=1)])

    updated = await UpdateComment(comments).execute(
        USER, 1, 1, CommentUpdateData(body="edited")
    )

    assert updated.body == "edited"


async def test_update_comment_missing_raises_not_found() -> None:
    with pytest.raises(CommentNotFound):
        await UpdateComment(FakeCommentRepository()).execute(
            USER, 1, 1, CommentUpdateData(body="x")
        )


async def test_update_comment_under_the_wrong_task_raises_not_found() -> None:
    comments = FakeCommentRepository([_comment(1, task_id=1)])

    with pytest.raises(CommentNotFound):
        await UpdateComment(comments).execute(USER, 2, 1, CommentUpdateData(body="x"))


async def test_delete_comment_missing_raises_not_found() -> None:
    with pytest.raises(CommentNotFound):
        await DeleteComment(FakeCommentRepository()).execute(USER, 1, 1)


async def test_delete_comment_removes_it() -> None:
    comments = FakeCommentRepository([_comment(1, task_id=1)])

    await DeleteComment(comments).execute(USER, 1, 1)

    assert await comments.get(USER, 1) is None


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


async def test_authenticate_as_demo_issues_a_token_pair() -> None:
    tokens = await _authenticate(_user()).execute_for_demo()

    assert tokens.access == f"access:{USER}"
    assert tokens.refresh == f"refresh:{USER}"


async def test_authenticate_as_demo_fails_when_the_demo_user_is_missing() -> None:
    with pytest.raises(UseCaseError):
        await _authenticate(None).execute_for_demo()


def _register(existing: User | None = None) -> tuple[RegisterUser, FakeUserRepository]:
    users = FakeUserRepository([existing] if existing is not None else [])
    return RegisterUser(users, FakePasswordHasher(), FakeTokenIssuer()), users


async def test_register_creates_the_user_and_issues_tokens() -> None:
    use_case, users = _register()

    tokens = await use_case.execute("newbie", "a-good-password")

    created = await users.get_by_username("newbie")
    assert created is not None
    # Password is stored hashed, never in the clear.
    assert created.hashed_password == FakePasswordHasher().hash("a-good-password")
    assert tokens.access == f"access:{created.id}"
    assert tokens.refresh == f"refresh:{created.id}"


async def test_register_rejects_a_taken_username() -> None:
    use_case, _ = _register(_user())

    with pytest.raises(UsernameConflict):
        await use_case.execute("demo", "another-password")


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
