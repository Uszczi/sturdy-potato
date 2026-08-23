from collections.abc import Mapping
from typing import Any

from sqlalchemy import delete, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Project, Task, utcnow
from infrastructure.repositories._positioning import next_position_subquery
from use_cases.dtos import ProjectCreateData
from use_cases.entities import Project as ProjectEntity
from use_cases.workflow import Workflow

_ORDER = (col(Project.position), col(Project.name), col(Project.id))


def _to_entity(project: Project, task_count: int) -> ProjectEntity:
    assert project.id is not None
    return ProjectEntity(
        id=project.id,
        workspace_id=project.workspace_id,
        name=project.name,
        color=project.color,
        workflow=Workflow.from_dicts(project.workflow),
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

    async def _get_orm(self, workspace_id: int, pk: int) -> Project | None:
        project: Project | None = await self._session.scalar(
            select(Project).where(
                col(Project.workspace_id) == workspace_id, col(Project.id) == pk
            )
        )
        return project

    async def list_all(self, workspace_id: int) -> list[ProjectEntity]:
        statement = self._count_select.where(
            col(Project.workspace_id) == workspace_id
        ).order_by(*_ORDER)
        rows = (await self._session.execute(statement)).all()
        return [_to_entity(project, count) for project, count in rows]

    async def get(self, workspace_id: int, project_id: int) -> ProjectEntity | None:
        statement = self._count_select.where(
            col(Project.workspace_id) == workspace_id, col(Project.id) == project_id
        )
        row = (await self._session.execute(statement)).first()
        return _to_entity(row[0], row[1]) if row is not None else None

    async def exists(self, workspace_id: int, project_id: int) -> bool:
        statement = select(col(Project.id)).where(
            col(Project.workspace_id) == workspace_id, col(Project.id) == project_id
        )
        return (await self._session.scalar(statement)) is not None

    async def name_exists(
        self,
        workspace_id: int,
        name: str,
        *,
        exclude_id: int | None = None,
    ) -> bool:
        statement = select(col(Project.id)).where(
            col(Project.workspace_id) == workspace_id, col(Project.name) == name
        )
        if exclude_id is not None:
            statement = statement.where(col(Project.id) != exclude_id)
        return (await self._session.scalar(statement)) is not None

    async def create(
        self, workspace_id: int, data: ProjectCreateData, workflow: Workflow
    ) -> ProjectEntity:
        # Assign the next position inside the INSERT so concurrent creates can't
        # read the same max and land on the same slot.
        now = utcnow()
        statement = (
            insert(Project)
            .values(
                workspace_id=workspace_id,
                name=data.name,
                color=data.color,
                workflow=workflow.to_dicts(),
                position=next_position_subquery(
                    col(Project.position), col(Project.workspace_id), workspace_id
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
        self, workspace_id: int, project_id: int, changes: Mapping[str, Any]
    ) -> ProjectEntity | None:
        project = await self._get_orm(workspace_id, project_id)
        if project is None:
            return None
        for field, value in changes.items():
            setattr(project, field, value)
        self._session.add(project)
        await self._session.flush()
        return await self.get(workspace_id, project_id)

    async def set_workflow(
        self, workspace_id: int, project_id: int, workflow: Workflow
    ) -> ProjectEntity | None:
        project = await self._get_orm(workspace_id, project_id)
        if project is None:
            return None
        project.workflow = workflow.to_dicts()
        self._session.add(project)
        await self._session.flush()
        return await self.get(workspace_id, project_id)

    async def delete(self, workspace_id: int, project_id: int) -> bool:
        project = await self._get_orm(workspace_id, project_id)
        if project is None:
            return False
        # A project owns its tasks: deleting it deletes them. Their comments
        # follow via the comments -> todos ON DELETE CASCADE.
        await self._session.execute(
            delete(Task).where(col(Task.project_id) == project_id)
        )
        await self._session.delete(project)
        await self._session.flush()
        return True

    async def ordered_ids(self, workspace_id: int) -> list[int]:
        statement = (
            select(col(Project.id))
            .where(col(Project.workspace_id) == workspace_id)
            .order_by(*_ORDER)
        )
        return list(await self._session.scalars(statement))

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None:
        if not positions:
            return
        statement = select(Project).where(
            col(Project.workspace_id) == workspace_id, col(Project.id).in_(positions)
        )
        for project in await self._session.scalars(statement):
            assert project.id is not None
            project.position = positions[project.id]
        await self._session.flush()
