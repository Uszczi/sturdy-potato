from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository


class ListOpenTasks:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, *, limit: int | None) -> list[Todo]:
        return await self._tasks.list_open_for_user(user_id, limit=limit)
