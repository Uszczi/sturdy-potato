from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Todo
from use_cases.dtos import TaskCreateData
from use_cases.entities import Task


def _today() -> date:
    return datetime.now(UTC).date()


def _to_entity(todo: Todo) -> Task:
    assert todo.id is not None
    return Task(
        id=todo.id,
        user_id=todo.user_id,
        project_id=todo.project_id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        position=todo.position,
        due_date=todo.due_date,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


# Open tasks come first (completed False < True), open tasks keep their manual
# position order, and completed tasks show most-recently-completed first so a
# freshly ticked task lands at the top of the completed group.
_OPEN_POSITION = case((col(Todo.completed).is_(False), col(Todo.position)))
_COMPLETED_RECENCY = case((col(Todo.completed).is_(True), col(Todo.updated_at)))
_LIST_ORDER = (
    col(Todo.completed).asc(),
    _OPEN_POSITION.asc(),
    _COMPLETED_RECENCY.desc(),
    col(Todo.created_at).desc(),
    col(Todo.id).desc(),
)

# The manual-position ordering the reorder view and open list share.
_POSITION_ORDER = (
    col(Todo.position),
    col(Todo.created_at).desc(),
    col(Todo.id).desc(),
)


class TodoRepository:
    """SQLAlchemy-backed implementation of the ``TaskRepository`` port.

    Writes flush but do not commit; the Unit of Work owns the transaction so a
    use case's writes commit together (or not at all).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_orm(self, user_id: int, task_id: int) -> Todo | None:
        statement = select(Todo).where(
            col(Todo.user_id) == user_id, col(Todo.id) == task_id
        )
        todo: Todo | None = await self._session.scalar(statement)
        return todo

    async def list_all(self, user_id: int) -> list[Task]:
        statement = (
            select(Todo).where(col(Todo.user_id) == user_id).order_by(*_LIST_ORDER)
        )
        return [_to_entity(todo) for todo in await self._session.scalars(statement)]

    async def list_for_view(
        self, user_id: int, *, view: str, project_id: int | None
    ) -> list[Task]:
        statement = select(Todo).where(col(Todo.user_id) == user_id)
        if project_id is not None:
            statement = statement.where(col(Todo.project_id) == project_id)
        elif view == "inbox":
            statement = statement.where(col(Todo.project_id).is_(None))
        elif view == "today":
            statement = statement.where(col(Todo.due_date) == _today())
        elif view == "upcoming":
            statement = statement.where(
                col(Todo.due_date) > _today(),
                col(Todo.completed).is_(False),
            )
        statement = statement.order_by(
            col(Todo.position),
            col(Todo.completed),
            col(Todo.due_date),
            col(Todo.created_at).desc(),
            col(Todo.id).desc(),
        )
        return [_to_entity(todo) for todo in await self._session.scalars(statement)]

    async def list_open(self, user_id: int, *, limit: int | None) -> list[Task]:
        statement = (
            select(Todo)
            .where(col(Todo.user_id) == user_id, col(Todo.completed).is_(False))
            .order_by(*_POSITION_ORDER)
        )
        if limit is not None:
            statement = statement.limit(limit)
        return [_to_entity(todo) for todo in await self._session.scalars(statement)]

    async def count(self, user_id: int, *, completed: bool | None) -> int:
        statement = (
            select(func.count()).select_from(Todo).where(col(Todo.user_id) == user_id)
        )
        if completed is not None:
            statement = statement.where(col(Todo.completed) == completed)
        total: int | None = await self._session.scalar(statement)
        return total or 0

    async def get(self, user_id: int, task_id: int) -> Task | None:
        todo = await self._get_orm(user_id, task_id)
        return _to_entity(todo) if todo is not None else None

    async def create(self, user_id: int, data: TaskCreateData) -> Task:
        max_position: int | None = await self._session.scalar(
            select(func.max(col(Todo.position))).where(col(Todo.user_id) == user_id)
        )
        todo = Todo(
            user_id=user_id,
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            completed=data.completed,
            due_date=data.due_date,
            position=(max_position or -1) + 1,
        )
        self._session.add(todo)
        await self._session.flush()
        await self._session.refresh(todo)
        return _to_entity(todo)

    async def update(
        self, user_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> Task | None:
        todo = await self._get_orm(user_id, task_id)
        if todo is None:
            return None
        for field, value in changes.items():
            setattr(todo, field, value)
        self._session.add(todo)
        await self._session.flush()
        await self._session.refresh(todo)
        return _to_entity(todo)

    async def delete(self, user_id: int, task_id: int) -> bool:
        todo = await self._get_orm(user_id, task_id)
        if todo is None:
            return False
        await self._session.delete(todo)
        await self._session.flush()
        return True

    async def ordered_ids(self, user_id: int) -> list[int]:
        statement = (
            select(col(Todo.id))
            .where(col(Todo.user_id) == user_id)
            .order_by(*_POSITION_ORDER)
        )
        return list(await self._session.scalars(statement))

    async def set_positions(self, user_id: int, positions: Mapping[int, int]) -> None:
        if not positions:
            return
        statement = select(Todo).where(
            col(Todo.user_id) == user_id, col(Todo.id).in_(positions)
        )
        for todo in await self._session.scalars(statement):
            assert todo.id is not None
            todo.position = positions[todo.id]
        await self._session.flush()
