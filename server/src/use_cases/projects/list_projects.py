from infrastructure.repositories import ProjectRepository
from schemas.project import ProjectSchema


class ListProjects:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int) -> list[ProjectSchema]:
        return await self._projects.list_for_user(user_id)
