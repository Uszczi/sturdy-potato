from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


def register_sqlite_pragmas(target_engine: AsyncEngine) -> None:
    """Set the per-connection SQLite pragmas the app relies on.

    WAL lets readers run concurrently with a writer (instead of every access
    serializing), which matters when several Uvicorn workers share the file.
    ``foreign_keys=ON`` is off by default in SQLite and is per-connection, so it
    must be set on every new connection or the FK constraints are not enforced.
    """

    @event.listens_for(target_engine.sync_engine, "connect")
    def _set_pragmas(dbapi_connection: Any, _record: Any) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()


# ``timeout`` is SQLite's busy timeout (seconds): with several Uvicorn workers
# sharing one database file, a writer waits for the current one to finish
# instead of failing immediately with "database is locked".
engine = create_async_engine(settings.database_url, connect_args={"timeout": 30})
register_sqlite_pragmas(engine)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
