from use_cases.entities import Task
from use_cases.ports import TaskRepository


class ListTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int) -> list[Task]:
        return await self._tasks.list_all(user_id)
