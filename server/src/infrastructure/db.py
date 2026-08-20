from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

# ``timeout`` is SQLite's busy timeout (seconds): with several Uvicorn workers
# sharing one database file, a writer waits for the current one to finish
# instead of failing immediately with "database is locked".
engine = create_async_engine(settings.database_url, connect_args={"timeout": 30})

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
