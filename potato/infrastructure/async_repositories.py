from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from infrastructure.models import Project, Todo, User
from infrastructure.repositories import ProjectRepository, TodoRepository


class AsyncTodoRepository:
    def __init__(self, sync_repo: TodoRepository) -> None:
        self._sync_repo = sync_repo

    async def list_for_user(self, user: User) -> QuerySet[Todo]:
        return await sync_to_async(self._sync_repo.list_for_user)(user)

    async def get_for_user(self, user: User, task_id: int) -> Todo | None:
        return await sync_to_async(self._sync_repo.get_for_user)(user, task_id)

    async def get_project_for_user(self, user: User, project_id: int) -> Project | None:
        return await sync_to_async(self._sync_repo.get_project_for_user)(
            user, project_id
        )

    async def create_for_user(self, user: User, data: dict) -> Todo:
        return await sync_to_async(self._sync_repo.create_for_user)(user, data)

    async def reorder_for_user(self, user: User, ordered_ids: list[int]) -> bool:
        return await sync_to_async(self._sync_repo.reorder_for_user)(user, ordered_ids)

    async def update(self, task: Todo, data: dict) -> Todo:
        return await sync_to_async(self._sync_repo.update)(task, data)

    async def delete(self, task: Todo) -> None:
        return await sync_to_async(self._sync_repo.delete)(task)


class AsyncProjectRepository:
    def __init__(self, sync_repo: ProjectRepository) -> None:
        self._sync_repo = sync_repo

    async def list_for_user(self, user: User) -> QuerySet[Project]:
        return await sync_to_async(self._sync_repo.list_for_user)(user)

    async def get_for_user(self, user: User, project_id: int) -> Project | None:
        return await sync_to_async(self._sync_repo.get_for_user)(user, project_id)

    async def create_for_user(self, user: User, data: dict) -> Project:
        return await sync_to_async(self._sync_repo.create_for_user)(user, data)

    async def reorder_for_user(self, user: User, ordered_ids: list[int]) -> bool:
        return await sync_to_async(self._sync_repo.reorder_for_user)(user, ordered_ids)

    async def update(self, project: Project, data: dict) -> Project:
        return await sync_to_async(self._sync_repo.update)(project, data)

    async def delete(self, project: Project) -> None:
        return await sync_to_async(self._sync_repo.delete)(project)
