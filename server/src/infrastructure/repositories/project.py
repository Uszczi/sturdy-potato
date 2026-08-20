from collections.abc import Mapping
from typing import Any

from sqlalchemy import func, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Project, Task, utcnow
from infrastructure.repositories._positioning import next_position_subquery
from use_cases.dtos import ProjectCreateData
from use_cases.entities import Project as ProjectEntity

_ORDER = (col(Project.position), col(Project.name), col(Project.id))


def _to_entity(project: Project, task_count: int) -> ProjectEntity:
    assert project.id is not None
    return ProjectEntity(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        color=project.color,
        position=project.position,
        task_count=task_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


class ProjectRepository:
    """SQLAlchemy-backed implementation of the ``ProjectRepository`` port.

    Writes flush but do not commit; the Unit of Work owns the transaction.
    """

    # Project reads carry a task_count aggregate, so they select the project
    # alongside a LEFT JOIN count of its tasks.
    _count_select = (
        select(Project, func.count(col(Task.id)))
        .outerjoin(Task, col(Task.project_id) == col(Project.id))
        .group_by(col(Project.id))
    )

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_orm(self, user_id: int, pk: int) -> Project | None:
        project: Project | None = await self._session.scalar(
            select(Project).where(
                col(Project.user_id) == user_id, col(Project.id) == pk
            )
        )
        return project

    async def list_all(self, user_id: int) -> list[ProjectEntity]:
        statement = self._count_select.where(col(Project.user_id) == user_id).order_by(
            *_ORDER
        )
        rows = (await self._session.execute(statement)).all()
        return [_to_entity(project, count) for project, count in rows]

    async def get(self, user_id: int, project_id: int) -> ProjectEntity | None:
        statement = self._count_select.where(
            col(Project.user_id) == user_id, col(Project.id) == project_id
        )
        row = (await self._session.execute(statement)).first()
        return _to_entity(row[0], row[1]) if row is not None else None

    async def exists(self, user_id: int, project_id: int) -> bool:
        statement = select(col(Project.id)).where(
            col(Project.user_id) == user_id, col(Project.id) == project_id
        )
        return (await self._session.scalar(statement)) is not None

    async def name_exists(
        self,
        user_id: int,
        name: str,
        *,
        exclude_id: int | None = None,
    ) -> bool:
        statement = select(col(Project.id)).where(
            col(Project.user_id) == user_id, col(Project.name) == name
        )
        if exclude_id is not None:
            statement = statement.where(col(Project.id) != exclude_id)
        return (await self._session.scalar(statement)) is not None

    async def create(self, user_id: int, data: ProjectCreateData) -> ProjectEntity:
        # Assign the next position inside the INSERT so concurrent creates can't
        # read the same max and land on the same slot.
        now = utcnow()
        statement = (
            insert(Project)
            .values(
                user_id=user_id,
                name=data.name,
                color=data.color,
                position=next_position_subquery(
                    col(Project.position), col(Project.user_id), user_id
                ),
                created_at=now,
                updated_at=now,
            )
            .returning(Project)
        )
        project = (await self._session.scalars(statement)).one()
        # A freshly created project has no tasks yet.
        return _to_entity(project, 0)

    async def update(
        self, user_id: int, project_id: int, changes: Mapping[str, Any]
    ) -> ProjectEntity | None:
        project = await self._get_orm(user_id, project_id)
        if project is None:
            return None
        for field, value in changes.items():
            setattr(project, field, value)
        self._session.add(project)
        await self._session.flush()
        return await self.get(user_id, project_id)

    async def delete(self, user_id: int, project_id: int) -> bool:
        project = await self._get_orm(user_id, project_id)
        if project is None:
            return False
        # Mirror the previous ON DELETE SET NULL: detach the project's tasks
        # before removing it so they survive as unassigned todos.
        await self._session.execute(
            update(Task)
            .where(col(Task.project_id) == project_id)
            .values(project_id=None)
        )
        await self._session.delete(project)
        await self._session.flush()
        return True

    async def ordered_ids(self, user_id: int) -> list[int]:
        statement = (
            select(col(Project.id))
            .where(col(Project.user_id) == user_id)
            .order_by(*_ORDER)
        )
        return list(await self._session.scalars(statement))

    async def set_positions(self, user_id: int, positions: Mapping[int, int]) -> None:
        if not positions:
            return
        statement = select(Project).where(
            col(Project.user_id) == user_id, col(Project.id).in_(positions)
        )
        for project in await self._session.scalars(statement):
            assert project.id is not None
            project.position = positions[project.id]
        await self._session.flush()
