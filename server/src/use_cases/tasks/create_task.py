from use_cases.boards import workflow_for
from use_cases.dtos import TaskCreateData
from use_cases.entities import Task
from use_cases.ports import ProjectRepository, TaskRepository, WorkspaceRepository


class CreateTask:
    def __init__(
        self,
        tasks: TaskRepository,
        projects: ProjectRepository,
        workspaces: WorkspaceRepository,
    ) -> None:
        self._tasks = tasks
        self._projects = projects
        self._workspaces = workspaces

    async def execute(self, workspace_id: int, data: TaskCreateData) -> Task:
        # Resolving the board both validates the project reference and tells us
        # which statuses are on offer.
        workflow = await workflow_for(
            self._projects, self._workspaces, workspace_id, data.project_id
        )
        status = (
            workflow.assign_initial()
            if data.status is None
            else workflow.assign(data.status)
        )
        return await self._tasks.create(workspace_id, data, status)
