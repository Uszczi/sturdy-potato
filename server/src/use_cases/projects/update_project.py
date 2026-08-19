from infrastructure.repositories import ProjectRepository
from schemas.project import ProjectSchema, ProjectUpdateInput
from use_cases.exceptions import ProjectNameConflict, ProjectNotFound


class UpdateProject:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(
        self, user_id: int, project_id: int, data: ProjectUpdateInput
    ) -> ProjectSchema:
        payload = data.model_dump(exclude_unset=True)
        if "name" in payload and await self._projects.name_exists(
            user_id, payload["name"], exclude_id=project_id
        ):
            raise ProjectNameConflict()
        project = await self._projects.update(user_id, project_id, payload)
        if project is None:
            raise ProjectNotFound()
        return project
