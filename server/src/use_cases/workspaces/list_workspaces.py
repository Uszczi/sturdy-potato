from use_cases.entities import Workspace
from use_cases.ports import WorkspaceRepository


class ListWorkspaces:
    def __init__(self, workspaces: WorkspaceRepository) -> None:
        self._workspaces = workspaces

    async def execute(self, user_id: int) -> list[Workspace]:
        return await self._workspaces.list_for_user(user_id)
