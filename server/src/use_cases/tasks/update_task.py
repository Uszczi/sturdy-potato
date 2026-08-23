from use_cases.boards import workflow_for
from use_cases.dtos import TaskUpdateData
from use_cases.entities import Task
from use_cases.ports import ProjectRepository, TaskRepository, WorkspaceRepository
from use_cases.tasks._helpers import get_task_or_404


class UpdateTask:
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
        self, workspace_id: int, task_id: int, data: TaskUpdateData
    ) -> Task:
        # Existence check first so a missing task wins over a bad project ref.
        task = await get_task_or_404(self._tasks, workspace_id, task_id)
        changes = data.to_changes()
        if "status" in changes or "project_id" in changes:
            # Either edit can change which board the task sits on, so the status
            # is always settled against the board it will end up on.
            target_project = changes.get("project_id", task.project_id)
            workflow = await workflow_for(
                self._projects, self._workspaces, workspace_id, target_project
            )
            if "status" in changes:
                changes.update(workflow.assign(changes["status"]).as_changes())
            elif target_project != task.project_id:
                # Moved to another board without naming a status: carry the work
                # across by intent so a finished task doesn't reopen itself.
                changes.update(
                    workflow.adopt(task.status, is_done=task.is_done).as_changes()
                )
        updated = await self._tasks.update(workspace_id, task_id, changes)
        assert updated is not None  # existence checked above, same transaction
        return updated
