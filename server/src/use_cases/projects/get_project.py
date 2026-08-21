from use_cases.entities import Project
from use_cases.exceptions import ProjectNotFound
from use_cases.ports import ProjectRepository


class GetProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, workspace_id: int, project_id: int) -> Project:
        project = await self._projects.get(workspace_id, project_id)
        if project is None:
            raise ProjectNotFound()
        return project
