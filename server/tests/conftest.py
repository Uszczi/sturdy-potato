from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

import infrastructure.db as db_module
import infrastructure.models  # noqa: F401  (registers tables on SQLModel.metadata)
from infrastructure.rate_limit import login_rate_limiter
from main import app


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    # The auth rate limiter is process-global; clear it so counts from one test
    # never spill into the next (and the limit test starts from zero).
    login_rate_limiter.reset()


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    # A shared in-memory SQLite database (StaticPool keeps a single connection
    # so every session in the test sees the same data).
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_maker(
    engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch
) -> async_sessionmaker[AsyncSession]:
    maker = async_sessionmaker(engine, expire_on_commit=False)
    # Point the app's real get_session dependency at the test database.
    monkeypatch.setattr(db_module, "async_session_maker", maker)
    return maker


@pytest_asyncio.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
