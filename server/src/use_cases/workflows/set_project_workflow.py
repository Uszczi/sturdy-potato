from use_cases.dtos import WorkflowUpdateData
from use_cases.entities import Project
from use_cases.exceptions import ProjectNotFound
from use_cases.ports import ProjectRepository, TaskRepository
from use_cases.workflow import Workflow
from use_cases.workflows._apply import apply_workflow


class SetProjectWorkflow:
    """Replace a project board's whole workflow in one go.

    Add, rename, reorder and remove all arrive together because the invariants
    ("exactly one initial, at least one terminal") only hold for a finished list
    — a sequence of granular edits would have to pass through states that break
    them.
    """

    def __init__(self, projects: ProjectRepository, tasks: TaskRepository) -> None:
        self._projects = projects
        self._tasks = tasks

    async def execute(
        self, workspace_id: int, project_id: int, data: WorkflowUpdateData
    ) -> Project:
        project = await self._projects.get(workspace_id, project_id)
        if project is None:
            raise ProjectNotFound()
        workflow = Workflow(data.statuses)
        # Re-settle the tasks before the old statuses stop existing.
        await apply_workflow(
            self._tasks,
            workspace_id,
            project_id,
            old=project.workflow,
            new=workflow,
            reassign=data.reassign,
        )
        updated = await self._projects.set_workflow(workspace_id, project_id, workflow)
        assert updated is not None  # existence checked above, same transaction
        return updated
