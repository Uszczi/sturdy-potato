from use_cases.dtos import TaskCreateData
from use_cases.entities import Task
from use_cases.ports import ProjectRepository, TaskRepository
from use_cases.tasks._helpers import ensure_project


class CreateTask:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository) -> None:
        self._tasks = tasks
        self._projects = projects

    async def execute(self, workspace_id: int, data: TaskCreateData) -> Task:
        await ensure_project(self._projects, workspace_id, data.project_id)
        return await self._tasks.create(workspace_id, data)
