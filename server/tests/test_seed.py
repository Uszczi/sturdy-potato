from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select

from cli import seed as seed_module
from infrastructure.models import Project, Task, User
from tests.factories import create_user

_EXPECTED_TODOS = sum(len(todos) for _, todos in seed_module.SEEDED_PROJECTS)


async def test_seed_creates_demo_user_and_data(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed(session_maker)

    user = await session.scalar(
        select(User).where(User.username == seed_module.DEMO_USERNAME)
    )
    assert user is not None
    projects = list(await session.scalars(select(Project)))
    todos = list(await session.scalars(select(Task)))
    assert len(projects) == len(seed_module.SEEDED_PROJECTS)
    assert len(todos) == _EXPECTED_TODOS


async def test_seed_is_idempotent(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed(session_maker)
    # Second run exercises the "already exists" branches for user/projects/todos.
    await seed_module.seed(session_maker)

    users = list(await session.scalars(select(User)))
    todos = list(await session.scalars(select(Task)))
    assert len(users) == 1
    assert len(todos) == _EXPECTED_TODOS


async def test_seed_demo_user_creates_then_finds(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed_demo_user("visitor", "pw-123", session_maker)
    # Second run exercises the "already exists" branch without seeding data.
    await seed_module.seed_demo_user("visitor", "pw-123", session_maker)

    users = list(await session.scalars(select(User).where(User.username == "visitor")))
    assert len(users) == 1
    assert list(await session.scalars(select(Project))) == []


def test_heavy_task_counts_ramp_from_one_to_max() -> None:
    assert seed_module._heavy_task_counts(1, 1000) == [1000]
    counts = seed_module._heavy_task_counts(4, 10)
    assert counts[0] == 1
    assert counts[-1] == 10
    assert counts == sorted(counts)


async def test_seed_heavy_creates_projects_with_growing_tasks(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed_heavy(
        "heavy", "pw-123", 3, 5, completed_ratio=1.0, session_maker=session_maker
    )

    projects = list(await session.scalars(select(Project)))
    todos = list(await session.scalars(select(Task)))
    assert len(projects) == 3
    # Counts ramp 1 -> 5 across 3 projects: [1, 3, 5] = 9 tasks.
    assert len(todos) == sum(seed_module._heavy_task_counts(3, 5))
    assert len(todos) == 9
    # completed_ratio=1.0 marks every task complete.
    assert all(todo.completed for todo in todos)


async def test_seed_heavy_completed_ratio_zero_leaves_tasks_open(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed_heavy(
        "heavy", "pw-123", 3, 5, completed_ratio=0.0, session_maker=session_maker
    )

    todos = list(await session.scalars(select(Task)))
    assert todos
    assert not any(todo.completed for todo in todos)
    # A reproducible seed spreads some tasks across due dates.
    assert any(todo.due_date is not None for todo in todos)


async def test_seed_heavy_skips_when_already_seeded(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed_heavy("heavy", "pw-123", 3, 5, session_maker=session_maker)
    # Re-running must not duplicate projects for the same user.
    await seed_module.seed_heavy("heavy", "pw-123", 3, 5, session_maker=session_maker)

    assert len(list(await session.scalars(select(Project)))) == 3
    assert len(list(await session.scalars(select(User)))) == 1


async def test_seed_admin_creates_active_staff_user(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed_admin("boss", "secret-123", session_maker)

    user = await session.scalar(select(User).where(User.username == "boss"))
    assert user is not None
    assert user.is_active
    assert user.is_staff


async def test_seed_admin_promotes_existing_user(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await create_user(session, username="boss", is_active=False, is_staff=False)

    await seed_module.seed_admin("boss", "secret-123", session_maker)

    users = list(await session.scalars(select(User).where(User.username == "boss")))
    assert len(users) == 1
    await session.refresh(users[0])
    assert users[0].is_active
    assert users[0].is_staff
