from fastapi import APIRouter, status

from api.dependencies import (
    CreateWorkspaceDep,
    GetWorkspaceDep,
    ListWorkspacesDep,
    SetWorkspaceWorkflowDep,
)
from auth import CurrentUserId, PathWorkspaceId
from schemas.workflow import WorkflowInput
from schemas.workspace import (
    WorkspaceCreateInput,
    WorkspaceDetailSchema,
    WorkspaceSchema,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("/", operation_id="api_workspaces_list")
async def list_workspaces(
    user_id: CurrentUserId, use_case: ListWorkspacesDep
) -> list[WorkspaceSchema]:
    workspaces = await use_case.execute(user_id)
    return [WorkspaceSchema.model_validate(workspace) for workspace in workspaces]


@router.post(
    "/", status_code=status.HTTP_201_CREATED, operation_id="api_workspaces_create"
)
async def create_workspace(
    body: WorkspaceCreateInput, user_id: CurrentUserId, use_case: CreateWorkspaceDep
) -> WorkspaceSchema:
    workspace = await use_case.execute(user_id, body.name)
    return WorkspaceSchema.model_validate(workspace)


@router.get("/{workspace_id}/", operation_id="api_workspaces_retrieve")
async def retrieve_workspace(
    workspace_id: PathWorkspaceId, use_case: GetWorkspaceDep
) -> WorkspaceDetailSchema:
    """One workspace, including the workflow the inbox board renders."""
    workspace = await use_case.execute(workspace_id)
    return WorkspaceDetailSchema.model_validate(workspace)


@router.put("/{workspace_id}/statuses/", operation_id="api_workspaces_statuses_update")
async def set_workspace_workflow(
    body: WorkflowInput,
    workspace_id: PathWorkspaceId,
    use_case: SetWorkspaceWorkflowDep,
) -> WorkspaceDetailSchema:
    """Replace the inbox board's workflow, and the template new projects copy.

    Projects that already exist keep their own snapshot and are untouched.
    """
    workspace = await use_case.execute(workspace_id, body.to_domain())
    return WorkspaceDetailSchema.model_validate(workspace)
