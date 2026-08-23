from use_cases.dtos import ProjectCreateData
from use_cases.entities import Project
from use_cases.exceptions import ProjectNameConflict, WorkspaceNotFound
from use_cases.ports import ProjectRepository, WorkspaceRepository


class CreateProject:
    def __init__(
        self, projects: ProjectRepository, workspaces: WorkspaceRepository
    ) -> None:
        self._projects = projects
        self._workspaces = workspaces

    async def execute(self, workspace_id: int, data: ProjectCreateData) -> Project:
        if await self._projects.name_exists(workspace_id, data.name):
            raise ProjectNameConflict()
        workspace = await self._workspaces.get(workspace_id)
        if workspace is None:
            raise WorkspaceNotFound()
        # A snapshot, not a reference: later edits to the workspace's default
        # leave this project's board alone.
        return await self._projects.create(workspace_id, data, workspace.workflow)
