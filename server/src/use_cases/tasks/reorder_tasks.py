from use_cases.ports import TaskRepository
from use_cases.reorder import apply_reorder


class ReorderTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, order: list[int]) -> None:
        await apply_reorder(self._tasks, user_id, order, noun="tasks")
