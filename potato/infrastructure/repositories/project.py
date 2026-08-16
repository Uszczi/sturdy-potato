from collections.abc import Mapping
from typing import Any

from django.db import transaction
from django.db.models import Count, Max, QuerySet

from infrastructure.models import Project, User


class ProjectRepository:
    def list_for_user(self, user: User) -> QuerySet[Project]:
        return (
            Project.objects.filter(user=user)
            .annotate(task_count=Count("tasks"))
            .order_by("position", "name", "id")
        )

    def get_for_user(self, user: User, project_id: int) -> Project | None:
        return (
            Project.objects.filter(user=user, id=project_id)
            .annotate(task_count=Count("tasks"))
            .first()
        )

    def create_for_user(self, user: User, data: Mapping[str, Any]) -> Project:
        project_data = dict(data)
        project_data.setdefault(
            "position",
            (
                Project.objects.filter(user=user).aggregate(
                    max_position=Max("position")
                )["max_position"]
                or -1
            )
            + 1,
        )
        project = Project.objects.create(user=user, **project_data)
        return self.get_for_user(user, project.id) or project

    def reorder_for_user(self, user: User, ordered_ids: list[int]) -> bool:
        projects = list(
            Project.objects.filter(user=user).order_by("position", "name", "id")
        )
        projects_by_id = {project.id: project for project in projects}
        if len(set(ordered_ids)) != len(ordered_ids) or not set(ordered_ids) <= set(
            projects_by_id
        ):
            return False

        slots = [
            index for index, project in enumerate(projects) if project.id in ordered_ids
        ]
        with transaction.atomic():
            updates = []
            for position, project_id in zip(slots, ordered_ids, strict=True):
                project = projects_by_id[project_id]
                project.position = position
                updates.append(project)
            if updates:
                Project.objects.bulk_update(updates, ["position"])
        return True

    def update(self, project: Project, data: Mapping[str, Any]) -> Project:
        for field, value in data.items():
            setattr(project, field, value)
        project.save()
        return self.get_for_user(project.user, project.id) or project

    def delete(self, project: Project) -> None:
        project.delete()
