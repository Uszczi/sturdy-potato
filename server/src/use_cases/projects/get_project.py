from infrastructure.repositories import ProjectRepository
from schemas.project import ProjectSchema
from use_cases.exceptions import ProjectNotFound


class GetProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int, project_id: int) -> ProjectSchema:
        project = await self._projects.get_for_user(user_id, project_id)
        if project is None:
            raise ProjectNotFound()
        return project
