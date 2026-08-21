from use_cases.ports import TaskRepository
from use_cases.task_status import TaskStatus


class CountTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, workspace_id: int, *, status: TaskStatus | None) -> int:
        return await self._tasks.count(workspace_id, status=status)
