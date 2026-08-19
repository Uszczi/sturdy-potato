from use_cases.dtos import ProjectCreateData
from use_cases.entities import Project
from use_cases.exceptions import ProjectNameConflict
from use_cases.ports import ProjectRepository


class CreateProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int, data: ProjectCreateData) -> Project:
        if await self._projects.name_exists(user_id, data.name):
            raise ProjectNameConflict()
        return await self._projects.create(user_id, data)
