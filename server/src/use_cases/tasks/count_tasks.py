from use_cases.ports import TaskRepository


class CountTasks:
    def __init__(self, tasks: TaskRepository) -> None:
        self._tasks = tasks

    async def execute(self, workspace_id: int, *, done: bool | None) -> int:
        # Counts are workspace-wide, spanning boards with different workflows, so
        # the filter is done-ness rather than any one status key.
        return await self._tasks.count(workspace_id, done=done)
