from infrastructure.repositories import ProjectRepository
from use_cases.exceptions import InvalidReorder


class ReorderProjects:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int, order: list[int]) -> None:
        if not await self._projects.reorder_for_user(user_id, order):
            raise InvalidReorder("Order contains projects outside this user.")
