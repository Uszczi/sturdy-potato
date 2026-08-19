from infrastructure.repositories import TodoRepository
from use_cases.exceptions import InvalidReorder


class ReorderTasks:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, order: list[int]) -> None:
        if not await self._tasks.reorder_for_user(user_id, order):
            raise InvalidReorder("Order contains tasks outside this user.")
