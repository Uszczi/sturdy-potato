"""Which Workflow governs a task.

A task's statuses come from the board it sits on: its project's Workflow, or the
workspace's own when it belongs to no project (the inbox). Every write that
touches a task's status resolves the board first, so a status is only ever
validated against the statuses that board actually offers.
"""

from use_cases.exceptions import ProjectNotFound, WorkspaceNotFound
from use_cases.ports import ProjectRepository, WorkspaceRepository
from use_cases.workflow import Workflow


async def workflow_for(
    projects: ProjectRepository,
    workspaces: WorkspaceRepository,
    workspace_id: int,
    project_id: int | None,
) -> Workflow:
    """The Workflow of the board a task in ``project_id`` belongs to.

    Doubles as the existence check for the project (or workspace), so callers
    don't need a separate one.
    """
    if project_id is None:
        workspace = await workspaces.get(workspace_id)
        if workspace is None:
            raise WorkspaceNotFound()
        return workspace.workflow
    project = await projects.get(workspace_id, project_id)
    if project is None:
        raise ProjectNotFound()
    return project.workflow
