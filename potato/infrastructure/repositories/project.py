from collections.abc import Mapping
from typing import Any

from django.db.models import Count, QuerySet

from infrastructure.models import Project, User


class ProjectRepository:
    def list_for_user(self, user: User) -> QuerySet[Project]:
        return (
            Project.objects.filter(user=user)
            .annotate(task_count=Count("tasks"))
            .order_by("name")
        )

    def get_for_user(self, user: User, project_id: int) -> Project | None:
        return (
            Project.objects.filter(user=user, id=project_id)
            .annotate(task_count=Count("tasks"))
            .first()
        )

    def create_for_user(self, user: User, data: Mapping[str, Any]) -> Project:
        project = Project.objects.create(user=user, **dict(data))
        return self.get_for_user(user, project.id) or project

    def update(self, project: Project, data: Mapping[str, Any]) -> Project:
        for field, value in data.items():
            setattr(project, field, value)
        project.save()
        return self.get_for_user(project.user, project.id) or project

    def delete(self, project: Project) -> None:
        project.delete()
