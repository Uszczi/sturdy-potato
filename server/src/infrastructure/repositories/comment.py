from collections.abc import Mapping
from typing import Any

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Comment, utcnow
from use_cases.dtos import CommentCreateData
from use_cases.entities import Comment as CommentEntity

# One task's comments read as a thread: oldest first, id breaking ties.
_THREAD_ORDER = (col(Comment.created_at), col(Comment.id))


def _to_entity(comment: Comment) -> CommentEntity:
    assert comment.id is not None
    return CommentEntity(
        id=comment.id,
        task_id=comment.task_id,
        user_id=comment.user_id,
        body=comment.body,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


class CommentRepository:
    """SQLAlchemy-backed implementation of the ``CommentRepository`` port.

    Writes flush but do not commit; the Unit of Work owns the transaction so a
    use case's writes commit together (or not at all).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_orm(self, user_id: int, comment_id: int) -> Comment | None:
        statement = select(Comment).where(
            col(Comment.user_id) == user_id, col(Comment.id) == comment_id
        )
        comment: Comment | None = await self._session.scalar(statement)
        return comment

    async def list_for_task(self, user_id: int, task_id: int) -> list[CommentEntity]:
        statement = (
            select(Comment)
            .where(col(Comment.user_id) == user_id, col(Comment.task_id) == task_id)
            .order_by(*_THREAD_ORDER)
        )
        return [_to_entity(c) for c in await self._session.scalars(statement)]

    async def get(self, user_id: int, comment_id: int) -> CommentEntity | None:
        comment = await self._get_orm(user_id, comment_id)
        return _to_entity(comment) if comment is not None else None

    async def create(
        self, user_id: int, task_id: int, data: CommentCreateData
    ) -> CommentEntity:
        now = utcnow()
        statement = (
            insert(Comment)
            .values(
                task_id=task_id,
                user_id=user_id,
                body=data.body,
                created_at=now,
                updated_at=now,
            )
            .returning(Comment)
        )
        comment = (await self._session.scalars(statement)).one()
        return _to_entity(comment)

    async def update(
        self, user_id: int, comment_id: int, changes: Mapping[str, Any]
    ) -> CommentEntity | None:
        comment = await self._get_orm(user_id, comment_id)
        if comment is None:
            return None
        for field, value in changes.items():
            setattr(comment, field, value)
        self._session.add(comment)
        await self._session.flush()
        await self._session.refresh(comment)
        return _to_entity(comment)

    async def delete(self, user_id: int, comment_id: int) -> bool:
        comment = await self._get_orm(user_id, comment_id)
        if comment is None:
            return False
        await self._session.delete(comment)
        await self._session.flush()
        return True
