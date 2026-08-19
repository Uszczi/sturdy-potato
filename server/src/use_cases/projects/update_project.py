from use_cases.dtos import ProjectUpdateData
from use_cases.entities import Project
from use_cases.exceptions import ProjectNameConflict, ProjectNotFound
from use_cases.ports import ProjectRepository


class UpdateProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(
        self, user_id: int, project_id: int, data: ProjectUpdateData
    ) -> Project:
        changes = data.to_changes()
        if "name" in changes and await self._projects.name_exists(
            user_id, changes["name"], exclude_id=project_id
        ):
            raise ProjectNameConflict()
        project = await self._projects.update(user_id, project_id, changes)
        if project is None:
            raise ProjectNotFound()
        return project
