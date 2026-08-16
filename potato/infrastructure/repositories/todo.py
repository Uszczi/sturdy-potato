from collections.abc import Mapping
from typing import Any

from django.db import transaction
from django.db.models import Max, QuerySet

from infrastructure.models import Project, Todo, User


class TodoRepository:
    def list_for_user(self, user: User) -> QuerySet[Todo]:
        return (
            Todo.objects.filter(user=user)
            .select_related("project")
            .order_by("position", "-created_at", "-id")
        )

    def get_project_for_user(self, user: User, project_id: int) -> Project | None:
        return Project.objects.filter(user=user, id=project_id).first()

    def get_for_user(self, user: User, task_id: int) -> Todo | None:
        return Todo.objects.filter(user=user, id=task_id).first()

    def create_for_user(self, user: User, data: Mapping[str, Any]) -> Todo:
        task_data = dict(data)
        task_data.setdefault(
            "position",
            (
                Todo.objects.filter(user=user).aggregate(max_position=Max("position"))[
                    "max_position"
                ]
                or -1
            )
            + 1,
        )
        return Todo.objects.create(user=user, **task_data)

    def reorder_for_user(self, user: User, ordered_ids: list[int]) -> bool:
        tasks = list(
            Todo.objects.filter(user=user).order_by("position", "-created_at", "-id")
        )
        tasks_by_id = {task.id: task for task in tasks}
        if len(set(ordered_ids)) != len(ordered_ids) or not set(ordered_ids) <= set(
            tasks_by_id
        ):
            return False

        slots = [index for index, task in enumerate(tasks) if task.id in ordered_ids]
        with transaction.atomic():
            updates = []
            for position, task_id in zip(slots, ordered_ids, strict=True):
                task = tasks_by_id[task_id]
                task.position = position
                updates.append(task)
            if updates:
                Todo.objects.bulk_update(updates, ["position"])
        return True

    def update(self, task: Todo, data: Mapping[str, Any]) -> Todo:
        for field, value in data.items():
            setattr(task, field, value)
        task.save()
        return task

    def delete(self, task: Todo) -> None:
        task.delete()
