from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from infrastructure.db import register_sqlite_pragmas


async def test_register_sqlite_pragmas_enables_wal_and_foreign_keys(
    tmp_path: Path,
) -> None:
    # WAL only applies to on-disk databases, so use a temp file rather than the
    # shared in-memory engine the rest of the suite uses.
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'pragmas.db'}")
    register_sqlite_pragmas(engine)
    try:
        async with engine.connect() as connection:
            journal_mode = await connection.scalar(text("PRAGMA journal_mode"))
            foreign_keys = await connection.scalar(text("PRAGMA foreign_keys"))
    finally:
        await engine.dispose()

    assert journal_mode == "wal"
    assert foreign_keys == 1
