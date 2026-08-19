from use_cases.dtos import TaskUpdateData
from use_cases.entities import Task
from use_cases.ports import ProjectRepository, TaskRepository
from use_cases.tasks._helpers import ensure_project, get_task_or_404


class UpdateTask:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository) -> None:
        self._tasks = tasks
        self._projects = projects

    async def execute(self, user_id: int, task_id: int, data: TaskUpdateData) -> Task:
        # Existence check first so a missing task wins over a bad project ref.
        await get_task_or_404(self._tasks, user_id, task_id)
        changes = data.to_changes()
        if "project_id" in changes:
            await ensure_project(self._projects, user_id, changes["project_id"])
        task = await self._tasks.update(user_id, task_id, changes)
        assert task is not None  # existence checked above, same transaction
        return task
