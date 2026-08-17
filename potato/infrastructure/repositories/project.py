from collections.abc import Mapping
from typing import Any

from django.db.models import Count, Max

from infrastructure.models import Project, User


class ProjectRepository:
    async def list_for_user(self, user: User) -> list[Project]:
        queryset = (
            Project.objects.filter(user=user)
            .annotate(task_count=Count("tasks"))
            .order_by("position", "name", "id")
        )
        return [project async for project in queryset]

    async def get_for_user(self, user: User, project_id: int) -> Project | None:
        return await (
            Project.objects.filter(user=user, id=project_id)
            .annotate(task_count=Count("tasks"))
            .afirst()
        )

    async def name_exists(
        self,
        user: User,
        name: str,
        *,
        exclude_id: int | None = None,
    ) -> bool:
        queryset = Project.objects.filter(user=user, name=name)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return await queryset.aexists()

    async def create_for_user(self, user: User, data: Mapping[str, Any]) -> Project:
        project_data = dict(data)
        if "position" not in project_data:
            aggregate = await Project.objects.filter(user=user).aaggregate(
                max_position=Max("position")
            )
            project_data["position"] = (aggregate["max_position"] or -1) + 1
        project = await Project.objects.acreate(user=user, **project_data)
        return await self.get_for_user(user, project.id) or project

    async def reorder_for_user(self, user: User, ordered_ids: list[int]) -> bool:
        queryset = Project.objects.filter(user=user).order_by("position", "name", "id")
        projects = [project async for project in queryset]
        projects_by_id = {project.id: project for project in projects}
        if len(set(ordered_ids)) != len(ordered_ids) or not set(ordered_ids) <= set(
            projects_by_id
        ):
            return False

        slots = [
            index for index, project in enumerate(projects) if project.id in ordered_ids
        ]
        updates = []
        for position, project_id in zip(slots, ordered_ids, strict=True):
            project = projects_by_id[project_id]
            project.position = position
            updates.append(project)
        if updates:
            await Project.objects.abulk_update(updates, ["position"])
        return True

    async def update(self, project: Project, data: Mapping[str, Any]) -> Project:
        for field, value in data.items():
            setattr(project, field, value)
        # Only write changed fields (plus auto_now) to avoid clobbering columns
        # touched by a concurrent request.
        await project.asave(update_fields=[*data, "updated_at"])
        refreshed = await (
            Project.objects.filter(id=project.id)
            .annotate(task_count=Count("tasks"))
            .afirst()
        )
        return refreshed or project

    async def delete(self, project: Project) -> None:
        await project.adelete()
