from use_cases.ports import TaskRepository
from use_cases.task_status import TaskStatus
from use_cases.tasks._helpers import get_task_or_404


class MoveTask:
    """Move a task to a status column and a slot within it, in one request.

    A task's position is scoped to its board column — one ``(project, status)``
    group — so a move only ever renumbers the destination column of the task's
    own project. The client sends the destination status and the index to drop
    the card at; the server rebuilds that column with the card inserted and
    renumbers it 0..N. This is the single path for both reordering within a
    column and flipping a card between the open and done columns.
    """

    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(
        self, user_id: int, task_id: int, status: TaskStatus, position: int
    ) -> None:
        task = await get_task_or_404(self._tasks, user_id, task_id)
        if task.status != status:
            await self._tasks.update(user_id, task_id, {"status": status})
        # The destination column (same project, target status) in its current
        # order, minus the moved task, with the card spliced back in at the
        # requested index (clamped to the end).
        column = [
            other.id
            for other in await self._tasks.list_all(user_id)
            if other.project_id == task.project_id
            and other.status == status
            and other.id != task_id
        ]
        column.insert(min(position, len(column)), task_id)
        await self._tasks.set_positions(
            user_id, {task_id: slot for slot, task_id in enumerate(column)}
        )
