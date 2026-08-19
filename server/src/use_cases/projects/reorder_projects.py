from use_cases.exceptions import InvalidReorder
from use_cases.ports import ProjectRepository


class ReorderProjects:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def execute(self, user_id: int, order: list[int]) -> None:
        current = await self._projects.ordered_ids(user_id)
        target = set(order)
        if len(target) != len(order) or not target <= set(current):
            raise InvalidReorder("Order contains projects outside this user.")
        slots = [index for index, pid in enumerate(current) if pid in target]
        positions = {pid: slot for slot, pid in zip(slots, order, strict=True)}
        await self._projects.set_positions(user_id, positions)
