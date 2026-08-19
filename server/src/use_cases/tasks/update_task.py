from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from schemas.todo import TodoUpdateInput
from use_cases.tasks._helpers import ensure_project, get_task_or_404


class UpdateTask:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, task_id: int, data: TodoUpdateInput) -> Todo:
        task = await get_task_or_404(self._tasks, user_id, task_id)
        payload = data.model_dump(exclude_unset=True)
        if "project_id" in payload:
            await ensure_project(self._tasks, user_id, payload["project_id"])
        return await self._tasks.update(task, payload)
