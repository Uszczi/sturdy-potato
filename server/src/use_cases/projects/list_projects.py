from use_cases.entities import Project
from use_cases.ports import ProjectRepository


class ListProjects:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int) -> list[Project]:
        return await self._projects.list_all(user_id)
