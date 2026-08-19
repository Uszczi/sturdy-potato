from use_cases.entities import Task
from use_cases.ports import TaskRepository
from use_cases.tasks._helpers import get_task_or_404


class GetTask:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, task_id: int) -> Task:
        return await get_task_or_404(self._tasks, user_id, task_id)
