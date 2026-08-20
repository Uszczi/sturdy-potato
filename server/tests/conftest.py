from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from redis.asyncio import from_url as redis_from_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

import infrastructure.cache as cache_module
import infrastructure.db as db_module
import infrastructure.models  # noqa: F401  (registers tables on SQLModel.metadata)
from infrastructure.rate_limit import login_rate_limiter
from main import app


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    # A throwaway PostgreSQL container backs the whole test session; each test
    # gets a freshly rebuilt schema (see the `engine` fixture) for isolation.
    with PostgresContainer("postgres:17-alpine") as postgres:
        # testcontainers hands back a psycopg2 URL; the app speaks asyncpg.
        yield postgres.get_connection_url().replace("+psycopg2", "+asyncpg")


@pytest.fixture(scope="session")
def redis_url() -> Iterator[str]:
    # A throwaway Redis container backs the whole test session; each test flushes
    # it (see the `redis_client` fixture) so cached values never leak across.
    with RedisContainer("redis:7-alpine") as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    # The auth rate limiter is process-global; clear it so counts from one test
    # never spill into the next (and the limit test starts from zero).
    login_rate_limiter.reset()


@pytest_asyncio.fixture
async def engine(postgres_url: str) -> AsyncIterator[AsyncEngine]:
    # Rebuild the schema per test so ids/sequences reset and no rows leak
    # between tests sharing the session-scoped database.
    engine = create_async_engine(postgres_url)
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await connection.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client(
    redis_url: str, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[Redis]:
    client: Redis = redis_from_url(redis_url, decode_responses=True)
    # Start from an empty cache and point the app's real get_redis dependency at
    # the test Redis.
    await client.flushdb()
    monkeypatch.setattr(cache_module, "redis_client", client)
    yield client
    await client.aclose()


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
