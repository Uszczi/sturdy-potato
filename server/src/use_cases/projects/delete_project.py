from use_cases.exceptions import ProjectNotFound
from use_cases.ports import ProjectRepository


class DeleteProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, workspace_id: int, project_id: int) -> None:
        if not await self._projects.delete(workspace_id, project_id):
            raise ProjectNotFound()
