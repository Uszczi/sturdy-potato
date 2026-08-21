from collections.abc import Mapping
from datetime import date
from typing import Any

from sqlalchemy import case, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Task, utcnow
from infrastructure.repositories._positioning import next_position_subquery
from use_cases.dtos import TaskCreateData
from use_cases.entities import Task as TaskEntity
from use_cases.task_status import TaskStatus


def _to_entity(task: Task) -> TaskEntity:
    assert task.id is not None
    return TaskEntity(
        id=task.id,
        user_id=task.user_id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=TaskStatus(task.status),
        position=task.position,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


# "Done" is the terminal status; everything else counts as still-open work.
_IS_DONE = case((col(Task.status) == TaskStatus.DONE, 1), else_=0)

# Open tasks come first (not-done sorts before done); within each group tasks
# keep their manual position order, so both the open and the done column can be
# reordered by drag-and-drop. When a task is completed the client reorders it to
# the top of the done group, keeping the "freshly ticked floats up" feel.
_LIST_ORDER = (
    _IS_DONE.asc(),
    col(Task.position).asc(),
    col(Task.created_at).desc(),
    col(Task.id).desc(),
)

# The manual-position ordering the reorder view and open list share.
_POSITION_ORDER = (
    col(Task.position),
    col(Task.created_at).desc(),
    col(Task.id).desc(),
)


class TaskRepository:
    """SQLAlchemy-backed implementation of the ``TaskRepository`` port.

    Writes flush but do not commit; the Unit of Work owns the transaction so a
    use case's writes commit together (or not at all).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_orm(self, user_id: int, task_id: int) -> Task | None:
        statement = select(Task).where(
            col(Task.user_id) == user_id, col(Task.id) == task_id
        )
        task: Task | None = await self._session.scalar(statement)
        return task

    async def list_all(self, user_id: int) -> list[TaskEntity]:
        statement = (
            select(Task).where(col(Task.user_id) == user_id).order_by(*_LIST_ORDER)
        )
        return [_to_entity(task) for task in await self._session.scalars(statement)]

    async def list_for_view(
        self, user_id: int, *, view: str, project_id: int | None, today: date
    ) -> list[TaskEntity]:
        statement = select(Task).where(col(Task.user_id) == user_id)
        if project_id is not None:
            statement = statement.where(col(Task.project_id) == project_id)
        elif view == "inbox":
            statement = statement.where(col(Task.project_id).is_(None))
        elif view == "today":
            statement = statement.where(col(Task.due_date) == today)
        elif view == "upcoming":
            statement = statement.where(
                col(Task.due_date) > today,
                col(Task.status) != TaskStatus.DONE,
            )
        statement = statement.order_by(
            col(Task.position),
            _IS_DONE,
            col(Task.due_date),
            col(Task.created_at).desc(),
            col(Task.id).desc(),
        )
        return [_to_entity(task) for task in await self._session.scalars(statement)]

    async def list_open(self, user_id: int, *, limit: int | None) -> list[TaskEntity]:
        statement = (
            select(Task)
            .where(col(Task.user_id) == user_id, col(Task.status) != TaskStatus.DONE)
            .order_by(*_POSITION_ORDER)
        )
        if limit is not None:
            statement = statement.limit(limit)
        return [_to_entity(task) for task in await self._session.scalars(statement)]

    async def count(self, user_id: int, *, status: TaskStatus | None) -> int:
        statement = (
            select(func.count()).select_from(Task).where(col(Task.user_id) == user_id)
        )
        if status is not None:
            statement = statement.where(col(Task.status) == status)
        total: int | None = await self._session.scalar(statement)
        return total or 0

    async def get(self, user_id: int, task_id: int) -> TaskEntity | None:
        task = await self._get_orm(user_id, task_id)
        return _to_entity(task) if task is not None else None

    async def create(self, user_id: int, data: TaskCreateData) -> TaskEntity:
        # Assign the next position inside the INSERT itself so the "read the max,
        # then write" gap can't hand two concurrent creates the same slot.
        now = utcnow()
        statement = (
            insert(Task)
            .values(
                user_id=user_id,
                project_id=data.project_id,
                title=data.title,
                description=data.description,
                status=data.status,
                due_date=data.due_date,
                position=next_position_subquery(
                    col(Task.position), col(Task.user_id), user_id
                ),
                created_at=now,
                updated_at=now,
            )
            .returning(Task)
        )
        task = (await self._session.scalars(statement)).one()
        return _to_entity(task)

    async def update(
        self, user_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> TaskEntity | None:
        task = await self._get_orm(user_id, task_id)
        if task is None:
            return None
        for field, value in changes.items():
            setattr(task, field, value)
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return _to_entity(task)

    async def delete(self, user_id: int, task_id: int) -> bool:
        task = await self._get_orm(user_id, task_id)
        if task is None:
            return False
        await self._session.delete(task)
        await self._session.flush()
        return True

    async def ordered_ids(self, user_id: int) -> list[int]:
        statement = (
            select(col(Task.id))
            .where(col(Task.user_id) == user_id)
            .order_by(*_POSITION_ORDER)
        )
        return list(await self._session.scalars(statement))

    async def set_positions(self, user_id: int, positions: Mapping[int, int]) -> None:
        if not positions:
            return
        statement = select(Task).where(
            col(Task.user_id) == user_id, col(Task.id).in_(positions)
        )
        for task in await self._session.scalars(statement):
            assert task.id is not None
            task.position = positions[task.id]
        await self._session.flush()
