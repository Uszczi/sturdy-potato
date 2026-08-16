from collections.abc import Mapping
from typing import Any

from django.db.models import Max
from django.utils import timezone

from infrastructure.models import Project, Todo, User


class TodoRepository:
    async def list_for_user(self, user: User) -> list[Todo]:
        queryset = (
            Todo.objects.filter(user=user)
            .select_related("project")
            .order_by("position", "-created_at", "-id")
        )
        return [task async for task in queryset]

    async def list_for_view(
        self,
        user: User,
        view: str = "inbox",
        project: Project | None = None,
    ) -> list[Todo]:
        queryset = Todo.objects.filter(user=user).select_related("project")
        if project is not None:
            queryset = queryset.filter(project=project)
        elif view == "inbox":
            queryset = queryset.filter(project__isnull=True)
        elif view == "today":
            queryset = queryset.filter(due_date=timezone.localdate())
        elif view == "upcoming":
            queryset = queryset.filter(
                due_date__gt=timezone.localdate(),
                completed=False,
            )
        queryset = queryset.order_by(
            "position", "completed", "due_date", "-created_at", "-id"
        )
        return [task async for task in queryset]

    async def list_open_for_user(
        self,
        user: User,
        limit: int | None = None,
    ) -> list[Todo]:
        queryset = (
            Todo.objects.filter(user=user, completed=False)
            .select_related("project")
            .order_by("position", "-created_at", "-id")
        )
        if limit is not None:
            queryset = queryset[:limit]
        return [task async for task in queryset]

    async def count_for_user(
        self,
        user: User,
        *,
        completed: bool | None = None,
    ) -> int:
        queryset = Todo.objects.filter(user=user)
        if completed is not None:
            queryset = queryset.filter(completed=completed)
        return await queryset.acount()

    async def get_project_for_user(
        self, user: User, project_id: int
    ) -> Project | None:
        return await Project.objects.filter(user=user, id=project_id).afirst()

    async def get_for_user(self, user: User, task_id: int) -> Todo | None:
        return await Todo.objects.filter(user=user, id=task_id).afirst()

    async def create_for_user(self, user: User, data: Mapping[str, Any]) -> Todo:
        task_data = dict(data)
        if "position" not in task_data:
            aggregate = await Todo.objects.filter(user=user).aaggregate(
                max_position=Max("position")
            )
            task_data["position"] = (aggregate["max_position"] or -1) + 1
        return await Todo.objects.acreate(user=user, **task_data)

    async def reorder_for_user(self, user: User, ordered_ids: list[int]) -> bool:
        queryset = Todo.objects.filter(user=user).order_by(
            "position", "-created_at", "-id"
        )
        tasks = [task async for task in queryset]
        tasks_by_id = {task.id: task for task in tasks}
        if len(set(ordered_ids)) != len(ordered_ids) or not set(ordered_ids) <= set(
            tasks_by_id
        ):
            return False

        slots = [index for index, task in enumerate(tasks) if task.id in ordered_ids]
        updates = []
        for position, task_id in zip(slots, ordered_ids, strict=True):
            task = tasks_by_id[task_id]
            task.position = position
            updates.append(task)
        if updates:
            await Todo.objects.abulk_update(updates, ["position"])
        return True

    async def update(self, task: Todo, data: Mapping[str, Any]) -> Todo:
        for field, value in data.items():
            setattr(task, field, value)
        await task.asave()
        return task

    async def delete(self, task: Todo) -> None:
        await task.adelete()
