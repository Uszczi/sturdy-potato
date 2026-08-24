from datetime import date
from itertools import count

from sqlalchemy.ext.asyncio import AsyncSession

from auth import WORKSPACE_HEADER
from infrastructure.models import (
    Comment,
    Project,
    Task,
    User,
    Workspace,
    WorkspaceMembership,
)
from infrastructure.security import password_hasher, token_service
from use_cases.workflow import DEFAULT_WORKFLOW, Workflow

_user_counter = count(1)
_workspace_counter = count(1)
_project_counter = count(1)
_task_counter = count(1)
_comment_counter = count(1)


async def create_user(
    session: AsyncSession,
    *,
    username: str | None = None,
    password: str = "password-123",
    is_active: bool = True,
    is_staff: bool = False,
) -> User:
    user = User(
        username=username or f"user-{next(_user_counter)}",
        hashed_password=password_hasher.hash(password),
        is_active=is_active,
        is_staff=is_staff,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_workspace(
    session: AsyncSession,
    user: User,
    *,
    name: str | None = None,
    is_personal: bool = True,
    workflow: Workflow = DEFAULT_WORKFLOW,
) -> Workspace:
    """A workspace owned by ``user`` (workspace + owner membership).

    Mirrors what registration mints for every new user, so seeded data behaves
    like the real thing.
    """
    workspace = Workspace(
        name=name or f"Workspace {next(_workspace_counter)}",
        workflow=workflow.to_dicts(),
        is_personal=is_personal,
    )
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)
    session.add(
        WorkspaceMembership(workspace_id=workspace.id, user_id=user.id, role="owner")
    )
    await session.commit()
    return workspace


async def create_user_with_workspace(
    session: AsyncSession, **kwargs: object
) -> tuple[User, Workspace]:
    """A user together with their personal workspace, the common setup."""
    user = await create_user(session, **kwargs)  # type: ignore[arg-type]
    workspace = await create_workspace(session, user)
    return user, workspace


async def add_member(
    session: AsyncSession, workspace: Workspace, user: User, *, role: str = "member"
) -> None:
    """Place an existing user into an existing workspace."""
    session.add(
        WorkspaceMembership(workspace_id=workspace.id, user_id=user.id, role=role)
    )
    await session.commit()


async def create_project(
    session: AsyncSession,
    workspace: Workspace,
    *,
    name: str | None = None,
    color: str | None = None,
    position: int = 0,
    workflow: Workflow = DEFAULT_WORKFLOW,
) -> Project:
    project = Project(
        workspace_id=workspace.id,
        name=name or f"Project {next(_project_counter)}",
        color=color,
        workflow=workflow.to_dicts(),
        position=position,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def create_task(
    session: AsyncSession,
    workspace: Workspace,
    *,
    title: str | None = None,
    description: str = "",
    status: str | None = None,
    position: int = 0,
    project: Project | None = None,
    due_date: date | None = None,
) -> Task:
    """A task on ``project``'s board (or the inbox), defaulting to its initial status.

    ``status`` names a key in that board's workflow; is_done is derived from it,
    so factory-made rows obey the same invariant the write paths do.
    """
    board = Workflow.from_dicts(
        project.workflow if project is not None else workspace.workflow
    )
    assignment = board.assign(status) if status is not None else board.assign_initial()
    task = Task(
        workspace_id=workspace.id,
        project_id=project.id if project is not None else None,
        title=title or f"Task {next(_task_counter)}",
        description=description,
        status=assignment.key,
        is_done=assignment.is_done,
        position=position,
        due_date=due_date,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def create_comment(
    session: AsyncSession,
    workspace: Workspace,
    user: User,
    task: Task,
    *,
    body: str | None = None,
) -> Comment:
    comment = Comment(
        task_id=task.id,
        workspace_id=workspace.id,
        user_id=user.id,
        body=body or f"Comment {next(_comment_counter)}",
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


def auth_headers(user: User, workspace: Workspace | None = None) -> dict[str, str]:
    """Bearer credentials for ``user``, optionally naming a workspace.

    Resource routes read the workspace from ``X-Workspace-Id`` and fall back to
    the caller's personal workspace, so most tests can leave it out; pass one
    when the target is not the caller's own (a shared workspace, or somebody
    else's, which must 404).
    """
    assert user.id is not None
    headers = {"Authorization": f"Bearer {token_service.access_token(user.id)}"}
    if workspace is not None:
        assert workspace.id is not None
        headers[WORKSPACE_HEADER] = str(workspace.id)
    return headers
