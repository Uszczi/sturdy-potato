from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from use_cases.tasks._helpers import ensure_project


class ViewTasks:
    def __init__(self, tasks: TodoRepository) -> None:
        self._tasks = tasks

    async def execute(
        self, user_id: int, *, view: str, project_id: int | None
    ) -> list[Todo]:
        await ensure_project(self._tasks, user_id, project_id)
        return await self._tasks.list_for_view(
            user_id, view=view, project_id=project_id
        )
