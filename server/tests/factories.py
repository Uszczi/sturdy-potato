from datetime import date
from itertools import count

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models import Project, Todo, User
from infrastructure.security import password_hasher, token_service

_user_counter = count(1)
_project_counter = count(1)
_task_counter = count(1)


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


async def create_project(
    session: AsyncSession,
    user: User,
    *,
    name: str | None = None,
    color: str | None = None,
    position: int = 0,
) -> Project:
    project = Project(
        user_id=user.id,
        name=name or f"Project {next(_project_counter)}",
        color=color,
        position=position,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def create_task(
    session: AsyncSession,
    user: User,
    *,
    title: str | None = None,
    description: str = "",
    completed: bool = False,
    position: int = 0,
    project: Project | None = None,
    due_date: date | None = None,
) -> Todo:
    task = Todo(
        user_id=user.id,
        project_id=project.id if project is not None else None,
        title=title or f"Task {next(_task_counter)}",
        description=description,
        completed=completed,
        position=position,
        due_date=due_date,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


def auth_headers(user: User) -> dict[str, str]:
    assert user.id is not None
    return {"Authorization": f"Bearer {token_service.access_token(user.id)}"}
