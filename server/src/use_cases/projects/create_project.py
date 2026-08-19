from infrastructure.repositories import ProjectRepository
from schemas.project import ProjectCreateInput, ProjectSchema
from use_cases.exceptions import ProjectNameConflict


class CreateProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int, data: ProjectCreateInput) -> ProjectSchema:
        if await self._projects.name_exists(user_id, data.name):
            raise ProjectNameConflict()
        return await self._projects.create_for_user(user_id, data.model_dump())
