from use_cases.boards import workflow_for
from use_cases.ports import ProjectRepository, TaskRepository, WorkspaceRepository
from use_cases.tasks._helpers import get_task_or_404


class MoveTask:
    """Move a task to a status column and a slot within it, in one request.

    A task's position is scoped to its board column — one ``(project, status)``
    group — so a move only ever renumbers the destination column of the task's
    own project. The client sends the destination status and the index to drop
    the card at; the server rebuilds that column with the card inserted and
    renumbers it 0..N. This is the single path for both reordering within a
    column and dragging a card between two columns of the same board.
    """

    def __init__(
        self,
        tasks: TaskRepository,
        projects: ProjectRepository,
        workspaces: WorkspaceRepository,
    ) -> None:
        self._tasks = tasks
        self._projects = projects
        self._workspaces = workspaces

    async def execute(
        self, workspace_id: int, task_id: int, status: str, position: int
    ) -> None:
        task = await get_task_or_404(self._tasks, workspace_id, task_id)
        # A drag can only land on a column this board actually shows.
        workflow = await workflow_for(
            self._projects, self._workspaces, workspace_id, task.project_id
        )
        assignment = workflow.assign(status)
        if task.status != assignment.key:
            await self._tasks.update(workspace_id, task_id, assignment.as_changes())
        # The destination column (same project, target status) in its current
        # order, minus the moved task, with the card spliced back in at the
        # requested index (clamped to the end).
        column = [
            other.id
            for other in await self._tasks.list_all(workspace_id)
            if other.project_id == task.project_id
            and other.status == assignment.key
            and other.id != task_id
        ]
        column.insert(min(position, len(column)), task_id)
        await self._tasks.set_positions(
            workspace_id, {task_id: slot for slot, task_id in enumerate(column)}
        )
