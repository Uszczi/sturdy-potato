from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Project, Todo


def _today() -> date:
    return datetime.now(UTC).date()


class TodoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: int) -> list[Todo]:
        statement = (
            select(Todo)
            .where(col(Todo.user_id) == user_id)
            .order_by(
                col(Todo.position), col(Todo.created_at).desc(), col(Todo.id).desc()
            )
        )
        return list(await self._session.scalars(statement))

    async def list_for_view(
        self,
        user_id: int,
        view: str = "inbox",
        project_id: int | None = None,
    ) -> list[Todo]:
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
        return list(await self._session.scalars(statement))

    async def list_open_for_user(
        self,
        user_id: int,
        limit: int | None = None,
    ) -> list[Todo]:
        statement = (
            select(Todo)
            .where(col(Todo.user_id) == user_id, col(Todo.completed).is_(False))
            .order_by(
                col(Todo.position), col(Todo.created_at).desc(), col(Todo.id).desc()
            )
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(await self._session.scalars(statement))

    async def count_for_user(
        self,
        user_id: int,
        *,
        completed: bool | None = None,
    ) -> int:
        statement = (
            select(func.count()).select_from(Todo).where(col(Todo.user_id) == user_id)
        )
        if completed is not None:
            statement = statement.where(col(Todo.completed) == completed)
        total: int | None = await self._session.scalar(statement)
        return total or 0

    async def get_project_for_user(
        self, user_id: int, project_id: int
    ) -> Project | None:
        statement = select(Project).where(
            col(Project.user_id) == user_id, col(Project.id) == project_id
        )
        project: Project | None = await self._session.scalar(statement)
        return project

    async def get_for_user(self, user_id: int, task_id: int) -> Todo | None:
        statement = select(Todo).where(
            col(Todo.user_id) == user_id, col(Todo.id) == task_id
        )
        task: Todo | None = await self._session.scalar(statement)
        return task

    async def create_for_user(
        self, user_id: int, data: Mapping[str, Any]
    ) -> Todo:
        task_data = dict(data)
        if "position" not in task_data:
            max_position: int | None = await self._session.scalar(
                select(func.max(col(Todo.position))).where(col(Todo.user_id) == user_id)
            )
            task_data["position"] = (max_position or -1) + 1
        task = Todo(user_id=user_id, **task_data)
        self._session.add(task)
        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def reorder_for_user(self, user_id: int, ordered_ids: list[int]) -> bool:
        statement = (
            select(Todo)
            .where(col(Todo.user_id) == user_id)
            .order_by(
                col(Todo.position), col(Todo.created_at).desc(), col(Todo.id).desc()
            )
        )
        tasks = list(await self._session.scalars(statement))
        tasks_by_id = {task.id: task for task in tasks}
        if len(set(ordered_ids)) != len(ordered_ids) or not set(ordered_ids) <= set(
            tasks_by_id
        ):
            return False

        slots = [index for index, task in enumerate(tasks) if task.id in ordered_ids]
        for position, task_id in zip(slots, ordered_ids, strict=True):
            tasks_by_id[task_id].position = position
        await self._session.commit()
        return True

    async def update(self, task: Todo, data: Mapping[str, Any]) -> Todo:
        for field, value in data.items():
            setattr(task, field, value)
        self._session.add(task)
        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def delete(self, task: Todo) -> None:
        await self._session.delete(task)
        await self._session.commit()
