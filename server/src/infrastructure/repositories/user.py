from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import User
from use_cases.entities import User as UserEntity


def _to_entity(user: User) -> UserEntity:
    assert user.id is not None
    return UserEntity(
        id=user.id,
        username=user.username,
        hashed_password=user.hashed_password,
        is_active=user.is_active,
        is_staff=user.is_staff,
    )


class UserRepository:
    """SQLAlchemy-backed implementation of the ``UserRepository`` port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_username(self, username: str) -> UserEntity | None:
        user: User | None = await self._session.scalar(
            select(User).where(col(User.username) == username)
        )
        return _to_entity(user) if user is not None else None

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        user = await self._session.get(User, user_id)
        return _to_entity(user) if user is not None else None
