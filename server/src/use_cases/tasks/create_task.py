from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from schemas.todo import TodoCreateInput
from use_cases.tasks._helpers import ensure_project


class CreateTask:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(self, user_id: int, data: TodoCreateInput) -> Todo:
        payload = data.model_dump()
        await ensure_project(self._tasks, user_id, payload["project_id"])
        return await self._tasks.create_for_user(user_id, payload)
