from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

# ``pool_pre_ping`` issues a lightweight liveness check before handing out a
# pooled connection, so a PostgreSQL connection dropped by the server (idle
# timeout, restart, failover) is transparently replaced instead of surfacing a
# stale-connection error on the next request.
engine = create_async_engine(settings.database_url, pool_pre_ping=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
