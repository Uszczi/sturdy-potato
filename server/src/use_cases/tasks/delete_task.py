from use_cases.exceptions import TaskNotFound
from use_cases.ports import TaskRepository


class DeleteTask:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, task_id: int) -> None:
        if not await self._tasks.delete(user_id, task_id):
            raise TaskNotFound()
