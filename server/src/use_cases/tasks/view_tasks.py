from use_cases.entities import Task
from use_cases.ports import ProjectRepository, TaskRepository
from use_cases.tasks._helpers import ensure_project


class ViewTasks:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository) -> None:
        self._tasks = tasks
        self._projects = projects

    async def execute(
        self, user_id: int, *, view: str, project_id: int | None
    ) -> list[Task]:
        await ensure_project(self._projects, user_id, project_id)
        return await self._tasks.list_for_view(
            user_id, view=view, project_id=project_id
        )
