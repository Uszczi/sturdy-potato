from use_cases.dtos import WorkflowUpdateData
from use_cases.entities import Workspace
from use_cases.exceptions import WorkspaceNotFound
from use_cases.ports import TaskRepository, WorkspaceRepository
from use_cases.workflow import Workflow
from use_cases.workflows._apply import apply_workflow


class SetWorkspaceWorkflow:
    """Replace the workspace's workflow: the inbox board, and the new-project template.

    Existing projects hold their own snapshot and are deliberately untouched, so
    this only re-settles the tasks that belong to no project.
    """

    def __init__(self, workspaces: WorkspaceRepository, tasks: TaskRepository) -> None:
        self._workspaces = workspaces
        self._tasks = tasks

    async def execute(self, workspace_id: int, data: WorkflowUpdateData) -> Workspace:
        workspace = await self._workspaces.get(workspace_id)
        if workspace is None:
            raise WorkspaceNotFound()
        workflow = Workflow(data.statuses)
        await apply_workflow(
            self._tasks,
            workspace_id,
            None,
            old=workspace.workflow,
            new=workflow,
            reassign=data.reassign,
        )
        updated = await self._workspaces.set_workflow(workspace_id, workflow)
        assert updated is not None  # existence checked above, same transaction
        return updated
