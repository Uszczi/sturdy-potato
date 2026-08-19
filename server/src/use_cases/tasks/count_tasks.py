from use_cases.ports import TaskRepository


class CountTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, *, completed: bool | None) -> int:
        return await self._tasks.count(user_id, completed=completed)
