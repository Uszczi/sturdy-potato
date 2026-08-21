from fastapi import APIRouter, status

from api.dependencies import CreateWorkspaceDep, ListWorkspacesDep
from auth import CurrentUserId
from schemas.workspace import WorkspaceCreateInput, WorkspaceSchema

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
