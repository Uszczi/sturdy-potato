from collections.abc import Mapping
from typing import Any

from django.db.models import QuerySet

from infrastructure.models import Todo
from potato.models import User


class TodoRepository:
    def list_for_user(self, user: User) -> QuerySet[Todo]:
        return Todo.objects.filter(user=user).order_by("-created_at")

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
