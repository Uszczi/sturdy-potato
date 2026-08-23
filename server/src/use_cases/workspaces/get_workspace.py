from use_cases.entities import Workspace
from use_cases.exceptions import WorkspaceNotFound
from use_cases.ports import WorkspaceRepository


class GetWorkspace:
    def __init__(self, workspaces: WorkspaceRepository) -> None:
        self._workspaces = workspaces

    async def execute(self, workspace_id: int) -> Workspace:
        workspace = await self._workspaces.get(workspace_id)
        if workspace is None:
            raise WorkspaceNotFound()
        return workspace
