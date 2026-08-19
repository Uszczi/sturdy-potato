from use_cases.entities import Task
from use_cases.ports import TaskRepository


class ListOpenTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, *, limit: int | None) -> list[Task]:
        return await self._tasks.list_open(user_id, limit=limit)
