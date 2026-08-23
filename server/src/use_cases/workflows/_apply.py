"""Re-settling a board's tasks after its workflow changes.

Shared by the project and workspace workflow edits: both replace a board's whole
workflow at once, and both must leave every task on that board sitting in a
status the new workflow actually has.
"""

from collections import defaultdict
from collections.abc import Mapping

from use_cases.entities import Task
from use_cases.exceptions import InvalidWorkflow
from use_cases.ports import TaskRepository
from use_cases.workflow import Workflow


def _check_reassign(old: Workflow, new: Workflow, reassign: Mapping[str, str]) -> None:
    removed = [key for key in old.keys if not new.has(key)]
    missing = [key for key in removed if key not in reassign]
    if missing:
        raise InvalidWorkflow(
            f"Removing {', '.join(sorted(missing))} needs a status to move "
            f"its tasks to."
        )
    stray = [key for key in reassign if key not in removed]
    if stray:
        raise InvalidWorkflow(
            f"{', '.join(sorted(stray))} is not being removed, so it cannot be "
            f"reassigned."
        )
    unknown = [target for target in reassign.values() if not new.has(target)]
    if unknown:
        raise InvalidWorkflow(
            f"Cannot move tasks to {', '.join(sorted(unknown))}: no such status "
            f"in the new workflow."
        )


async def apply_workflow(
    tasks: TaskRepository,
    workspace_id: int,
    project_id: int | None,
    *,
    old: Workflow,
    new: Workflow,
    reassign: Mapping[str, str],
) -> None:
    """Move this board's tasks onto ``new``, renumbering the columns they land in.

    A status that survives the edit keeps its tasks (its done-ness is re-read
    from the new workflow, since a rename or a flag change can flip it). A status
    that is dropped hands its tasks to the ``reassign`` target the caller named.
    """
    _check_reassign(old, new, reassign)

    def old_column(task: Task) -> int:
        # Unknown keys sort last; merged columns then stack in workflow order
        # rather than interleaving by position.
        return old.keys.index(task.status) if old.has(task.status) else len(old.keys)

    board = sorted(
        (t for t in await tasks.list_all(workspace_id) if t.project_id == project_id),
        key=lambda t: (old_column(t), t.position, -t.id),
    )
    columns: dict[str, list[Task]] = defaultdict(list)
    landing = {
        task.id: new.adopt(reassign.get(task.status, task.status), is_done=task.is_done)
        for task in board
    }
    for task in board:
        columns[landing[task.id].key].append(task)

    for members in columns.values():
        for slot, task in enumerate(members):
            assignment = landing[task.id]
            if (task.status, task.is_done, task.position) == (
                assignment.key,
                assignment.is_done,
                slot,
            ):
                continue
            await tasks.update(
                workspace_id, task.id, {**assignment.as_changes(), "position": slot}
            )
