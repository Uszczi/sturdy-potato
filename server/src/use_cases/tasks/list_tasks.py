from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository


class ListTasks:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int) -> list[Todo]:
        return await self._tasks.list_for_user(user_id)
