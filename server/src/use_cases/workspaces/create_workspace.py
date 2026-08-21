from use_cases.entities import Workspace
from use_cases.ports import WorkspaceRepository


class CreateWorkspace:
    def __init__(self, workspaces: WorkspaceRepository) -> None:
        self._workspaces = workspaces

    async def execute(self, owner_id: int, name: str) -> Workspace:
        # User-created workspaces are never personal; the personal one is minted
        # once at registration.
        return await self._workspaces.create(owner_id, name, is_personal=False)
