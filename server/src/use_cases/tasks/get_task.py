from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from use_cases.tasks._helpers import get_task_or_404


class GetTask:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, task_id: int) -> Todo:
        return await get_task_or_404(self._tasks, user_id, task_id)
