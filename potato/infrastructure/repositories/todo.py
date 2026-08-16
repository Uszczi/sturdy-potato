from collections.abc import Mapping
from typing import Any

from django.db.models import QuerySet

from infrastructure.models import Project, Todo, User


class TodoRepository:
    def list_for_user(self, user: User) -> QuerySet[Todo]:
        return (
            Todo.objects.filter(user=user)
            .select_related("project")
            .order_by("-created_at")
        )

    def get_project_for_user(self, user: User, project_id: int) -> Project | None:
        return Project.objects.filter(user=user, id=project_id).first()

    def get_for_user(self, user: User, task_id: int) -> Todo | None:
        return Todo.objects.filter(user=user, id=task_id).first()

    def create_for_user(self, user: User, data: Mapping[str, Any]) -> Todo:
        return Todo.objects.create(user=user, **dict(data))

    def update(self, task: Todo, data: Mapping[str, Any]) -> Todo:
        for field, value in data.items():
            setattr(task, field, value)
        task.save()
        return task

    def delete(self, task: Todo) -> None:
        task.delete()
