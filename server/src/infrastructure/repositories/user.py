from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import User


class UserRepository:
    """Session-bound access to :class:`User` records.

    Unlike the stateless repositories, this one holds its session so routes can
    depend on the repository directly instead of threading a session through.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(col(User.username) == username)
        user: User | None = await self._session.scalar(statement)
        return user
