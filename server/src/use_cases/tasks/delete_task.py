from infrastructure.repositories import TodoRepository
from use_cases.tasks._helpers import get_task_or_404


class DeleteTask:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, task_id: int) -> None:
        task = await get_task_or_404(self._tasks, user_id, task_id)
        await self._tasks.delete(task)
