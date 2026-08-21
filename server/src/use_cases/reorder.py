"""The reorder rule, shared by tasks and projects.

Tasks and projects reorder identically: the client sends the ids it wants
rearranged, and they take over the position slots those same ids currently
occupy, in the requested order, leaving every other row untouched. The rule
lives here (not in SQL) so both use cases share one implementation.
"""

from collections.abc import Mapping
from typing import Protocol

from use_cases.exceptions import InvalidReorder


class Reorderable(Protocol):
    """A repository whose rows carry a per-workspace manual ordering."""

    async def ordered_ids(self, workspace_id: int) -> list[int]: ...

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None: ...


async def apply_reorder(
    repo: Reorderable, workspace_id: int, order: list[int], *, noun: str
) -> None:
    # The reordered ids must be a duplicate-free subset of the workspace's rows.
    current = await repo.ordered_ids(workspace_id)
    target = set(order)
    if len(target) != len(order) or not target <= set(current):
        raise InvalidReorder(f"Order contains {noun} outside this workspace.")
    slots = [index for index, row_id in enumerate(current) if row_id in target]
    positions = {row_id: slot for slot, row_id in zip(slots, order, strict=True)}
    await repo.set_positions(workspace_id, positions)
