"""Unit of Work: owns the transaction boundary for a request.

Repositories flush their writes but never commit. The Unit of Work holds the
session and commits once, so a use case that touches several repositories
commits atomically (or rolls back as a whole on error).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.repositories import ProjectRepository, TodoRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.tasks = TodoRepository(session)
        self.projects = ProjectRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
