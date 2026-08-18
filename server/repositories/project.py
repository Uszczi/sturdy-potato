from collections.abc import Mapping
from typing import Any

from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from models import Project, Todo
from schemas.project import ProjectSchema


def _to_schema(project: Project, task_count: int) -> ProjectSchema:
    schema = ProjectSchema.model_validate(project)
    schema.task_count = task_count
    return schema


class ProjectRepository:
    # Project reads carry a task_count aggregate, so they select the project
    # alongside a LEFT JOIN count of its tasks.
    _count_select = (
        select(Project, func.count(col(Todo.id)))
        .outerjoin(Todo, col(Todo.project_id) == col(Project.id))
        .group_by(col(Project.id))
    )

    async def _get_orm(
        self, session: AsyncSession, user_id: int, pk: int
    ) -> Project | None:
        project: Project | None = await session.scalar(
            select(Project).where(
                col(Project.user_id) == user_id, col(Project.id) == pk
            )
        )
        return project

    async def list_for_user(
        self, session: AsyncSession, user_id: int
    ) -> list[ProjectSchema]:
        statement = self._count_select.where(col(Project.user_id) == user_id).order_by(
            col(Project.position), col(Project.name), col(Project.id)
        )
        rows = (await session.execute(statement)).all()
        return [_to_schema(project, count) for project, count in rows]

    async def get_for_user(
        self, session: AsyncSession, user_id: int, pk: int
    ) -> ProjectSchema | None:
        statement = self._count_select.where(
            col(Project.user_id) == user_id, col(Project.id) == pk
        )
        row = (await session.execute(statement)).first()
        return _to_schema(row[0], row[1]) if row is not None else None

    async def name_exists(
        self,
        session: AsyncSession,
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
        return (await session.scalar(statement)) is not None

    async def create_for_user(
        self, session: AsyncSession, user_id: int, data: Mapping[str, Any]
    ) -> ProjectSchema:
        project_data = dict(data)
        if "position" not in project_data:
            max_position: int | None = await session.scalar(
                select(func.max(col(Project.position))).where(
                    col(Project.user_id) == user_id
                )
            )
            project_data["position"] = (max_position or -1) + 1
        project = Project(user_id=user_id, **project_data)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        assert project.id is not None
        created = await self.get_for_user(session, user_id, project.id)
        assert created is not None
        return created

    async def reorder_for_user(
        self, session: AsyncSession, user_id: int, ordered_ids: list[int]
    ) -> bool:
        statement = (
            select(Project)
            .where(col(Project.user_id) == user_id)
            .order_by(col(Project.position), col(Project.name), col(Project.id))
        )
        projects = list(await session.scalars(statement))
        projects_by_id = {project.id: project for project in projects}
        if len(set(ordered_ids)) != len(ordered_ids) or not set(ordered_ids) <= set(
            projects_by_id
        ):
            return False

        slots = [
            index for index, project in enumerate(projects) if project.id in ordered_ids
        ]
        for position, project_id in zip(slots, ordered_ids, strict=True):
            projects_by_id[project_id].position = position
        await session.commit()
        return True

    async def update(
        self, session: AsyncSession, user_id: int, pk: int, data: Mapping[str, Any]
    ) -> ProjectSchema | None:
        project = await self._get_orm(session, user_id, pk)
        if project is None:
            return None
        for field, value in data.items():
            setattr(project, field, value)
        session.add(project)
        await session.commit()
        return await self.get_for_user(session, user_id, pk)

    async def delete(self, session: AsyncSession, user_id: int, pk: int) -> bool:
        project = await self._get_orm(session, user_id, pk)
        if project is None:
            return False
        # Mirror the previous ON DELETE SET NULL: detach the project's tasks
        # before removing it so they survive as unassigned todos.
        await session.execute(
            update(Todo).where(col(Todo.project_id) == pk).values(project_id=None)
        )
        await session.delete(project)
        await session.commit()
        return True
