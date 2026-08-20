from use_cases.ports import ProjectRepository
from use_cases.reorder import apply_reorder


class ReorderProjects:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int, order: list[int]) -> None:
        await apply_reorder(self._projects, user_id, order, noun="projects")
