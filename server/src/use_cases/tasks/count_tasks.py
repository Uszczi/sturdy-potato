from infrastructure.repositories import TodoRepository


class CountTasks:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, *, completed: bool | None) -> int:
        return await self._tasks.count_for_user(user_id, completed=completed)
