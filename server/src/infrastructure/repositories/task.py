from collections.abc import Mapping
from datetime import date
from typing import Any

from sqlalchemy import func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Task, utcnow
from infrastructure.repositories._positioning import next_task_position_subquery
from use_cases.dtos import TaskCreateData
from use_cases.entities import Task as TaskEntity
from use_cases.workflow import StatusAssignment


def _to_entity(task: Task) -> TaskEntity:
    assert task.id is not None
    return TaskEntity(
        id=task.id,
        workspace_id=task.workspace_id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        is_done=task.is_done,
        position=task.position,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


# Which statuses count as finished is per-board, so ordering reads the
# denormalised flag rather than comparing against any particular status key.
_IS_DONE = col(Task.is_done)

# One board (a single project, or the inbox) in board order: unfinished cards
# first, then finished, and within each status column the manual position wins.
# Positions are scoped per column, so this only makes sense when the read is
# already limited to one project group.
_BOARD_ORDER = (
    _IS_DONE.asc(),
    col(Task.position).asc(),
    col(Task.id).desc(),
)

# Cross-project views (today/upcoming/all) span many columns, so no single
# position sequence orders them; fall back to due date then recency, open first.
_VIEW_ORDER = (
    _IS_DONE.asc(),
    col(Task.due_date),
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

    async def _get_orm(self, workspace_id: int, task_id: int) -> Task | None:
        statement = select(Task).where(
            col(Task.workspace_id) == workspace_id, col(Task.id) == task_id
        )
        task: Task | None = await self._session.scalar(statement)
        return task

    async def list_all(self, workspace_id: int) -> list[TaskEntity]:
        # A whole-workspace read spans every column, so group by project first
        # and only then apply board order inside each group.
        statement = (
            select(Task)
            .where(col(Task.workspace_id) == workspace_id)
            .order_by(col(Task.project_id), *_BOARD_ORDER)
        )
        return [_to_entity(task) for task in await self._session.scalars(statement)]

    async def list_for_view(
        self, workspace_id: int, *, view: str, project_id: int | None, today: date
    ) -> list[TaskEntity]:
        statement = select(Task).where(col(Task.workspace_id) == workspace_id)
        # A read limited to one project (or the inbox) is a single board, so it
        # can honour the per-column manual position; the cross-project views
        # can't, and fall back to due date + recency.
        scoped_to_one_board = project_id is not None or view == "inbox"
        if project_id is not None:
            statement = statement.where(col(Task.project_id) == project_id)
        elif view == "inbox":
            statement = statement.where(col(Task.project_id).is_(None))
        elif view == "today":
            statement = statement.where(col(Task.due_date) == today)
        elif view == "upcoming":
            statement = statement.where(
                col(Task.due_date) > today,
                _IS_DONE.is_(False),
            )
        order = _BOARD_ORDER if scoped_to_one_board else _VIEW_ORDER
        statement = statement.order_by(*order)
        return [_to_entity(task) for task in await self._session.scalars(statement)]

    async def list_open(
        self, workspace_id: int, *, limit: int | None
    ) -> list[TaskEntity]:
        # A bounded "next up" preview across projects; position is per-column now,
        # so this is only a stable-ish preview, tie-broken by newest id.
        statement = (
            select(Task)
            .where(
                col(Task.workspace_id) == workspace_id,
                _IS_DONE.is_(False),
            )
            .order_by(col(Task.position), col(Task.id).desc())
        )
        if limit is not None:
            statement = statement.limit(limit)
        return [_to_entity(task) for task in await self._session.scalars(statement)]

    async def count(self, workspace_id: int, *, done: bool | None) -> int:
        statement = (
            select(func.count())
            .select_from(Task)
            .where(col(Task.workspace_id) == workspace_id)
        )
        if done is not None:
            statement = statement.where(_IS_DONE.is_(done))
        total: int | None = await self._session.scalar(statement)
        return total or 0

    async def get(self, workspace_id: int, task_id: int) -> TaskEntity | None:
        task = await self._get_orm(workspace_id, task_id)
        return _to_entity(task) if task is not None else None

    async def create(
        self, workspace_id: int, data: TaskCreateData, status: StatusAssignment
    ) -> TaskEntity:
        # Assign the next slot in the target column inside the INSERT itself so
        # the "read the max, then write" gap can't hand two concurrent creates
        # the same slot.
        now = utcnow()
        statement = (
            insert(Task)
            .values(
                workspace_id=workspace_id,
                project_id=data.project_id,
                title=data.title,
                description=data.description,
                status=status.key,
                is_done=status.is_done,
                due_date=data.due_date,
                position=next_task_position_subquery(
                    workspace_id, data.project_id, status.key
                ),
                created_at=now,
                updated_at=now,
            )
            .returning(Task)
        )
        task = (await self._session.scalars(statement)).one()
        return _to_entity(task)

    async def update(
        self, workspace_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> TaskEntity | None:
        task = await self._get_orm(workspace_id, task_id)
        if task is None:
            return None
        for field, value in changes.items():
            setattr(task, field, value)
        # Changing project or status moves the task to a different column. Unless
        # the caller pinned an explicit slot (a drag, via ``set_positions``),
        # append it to the end of the destination column so it lands predictably
        # instead of keeping a stale position from the column it left.
        if (
            "project_id" in changes or "status" in changes
        ) and "position" not in changes:
            task.position = await self._next_position(
                workspace_id, task.project_id, task.status, exclude_id=task_id
            )
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return _to_entity(task)

    async def _next_position(
        self, workspace_id: int, project_id: int | None, status: str, *, exclude_id: int
    ) -> int:
        project_match = (
            col(Task.project_id).is_(None)
            if project_id is None
            else col(Task.project_id) == project_id
        )
        statement = select(func.coalesce(func.max(col(Task.position)), -1) + 1).where(
            col(Task.workspace_id) == workspace_id,
            project_match,
            col(Task.status) == status,
            col(Task.id) != exclude_id,
        )
        return (await self._session.scalar(statement)) or 0

    async def delete(self, workspace_id: int, task_id: int) -> bool:
        task = await self._get_orm(workspace_id, task_id)
        if task is None:
            return False
        await self._session.delete(task)
        await self._session.flush()
        return True

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None:
        if not positions:
            return
        statement = select(Task).where(
            col(Task.workspace_id) == workspace_id, col(Task.id).in_(positions)
        )
        for task in await self._session.scalars(statement):
            assert task.id is not None
            task.position = positions[task.id]
        await self._session.flush()
