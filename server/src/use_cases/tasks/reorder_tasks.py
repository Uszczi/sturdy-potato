from use_cases.exceptions import InvalidReorder
from use_cases.ports import TaskRepository


class ReorderTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, order: list[int]) -> None:
        # The reorder rule lives here, not in SQL: the reordered ids must be a
        # duplicate-free subset of the user's tasks. They then take over the
        # slots they currently occupy, in the requested order, leaving every
        # other task's position untouched.
        current = await self._tasks.ordered_ids(user_id)
        target = set(order)
        if len(target) != len(order) or not target <= set(current):
            raise InvalidReorder("Order contains tasks outside this user.")
        slots = [index for index, task_id in enumerate(current) if task_id in target]
        positions = {task_id: slot for slot, task_id in zip(slots, order, strict=True)}
        await self._tasks.set_positions(user_id, positions)
