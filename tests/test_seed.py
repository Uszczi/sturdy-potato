import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select

import seed as seed_module
from models import Project, Todo, User

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
    todos = list(await session.scalars(select(Todo)))
    assert len(projects) == len(seed_module.SEEDED_PROJECTS)
    assert len(todos) == _EXPECTED_TODOS


async def test_seed_is_idempotent(
    session_maker: async_sessionmaker[AsyncSession], session: AsyncSession
) -> None:
    await seed_module.seed(session_maker)
    # Second run exercises the "already exists" branches for user/projects/todos.
    await seed_module.seed(session_maker)

    users = list(await session.scalars(select(User)))
    todos = list(await session.scalars(select(Todo)))
    assert len(users) == 1
    assert len(todos) == _EXPECTED_TODOS


def test_main_invokes_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = False

    async def fake_seed() -> None:
        nonlocal ran
        ran = True

    monkeypatch.setattr(seed_module, "seed", fake_seed)
    seed_module.main()

    assert ran
