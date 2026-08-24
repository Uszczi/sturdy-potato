from fastapi import APIRouter, status

from api.dependencies import (
    CreateProjectDep,
    DeleteProjectDep,
    GetProjectDep,
    ListProjectsDep,
    ReorderProjectsDep,
    SetProjectWorkflowDep,
    UpdateProjectDep,
)
from auth import WorkspaceId
from schemas.order import ReorderInput
from schemas.project import (
    ProjectCreateInput,
    ProjectDetailSchema,
    ProjectSchema,
    ProjectUpdateInput,
)
from schemas.workflow import WorkflowInput

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", operation_id="api_projects_list")
async def list_projects(
    workspace_id: WorkspaceId, use_case: ListProjectsDep
) -> list[ProjectSchema]:
    projects = await use_case.execute(workspace_id)
    return [ProjectSchema.model_validate(project) for project in projects]


@router.post(
    "/", status_code=status.HTTP_201_CREATED, operation_id="api_projects_create"
)
async def create_project(
    body: ProjectCreateInput, workspace_id: WorkspaceId, use_case: CreateProjectDep
) -> ProjectSchema:
    project = await use_case.execute(workspace_id, body.to_domain())
    return ProjectSchema.model_validate(project)


@router.post(
    "/reorder/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_projects_reorder_create",
)
async def reorder_projects(
    body: ReorderInput, workspace_id: WorkspaceId, use_case: ReorderProjectsDep
) -> None:
    await use_case.execute(workspace_id, body.order)


@router.get("/{id}/", operation_id="api_projects_retrieve")
async def retrieve_project(
    id: int, workspace_id: WorkspaceId, use_case: GetProjectDep
) -> ProjectDetailSchema:
    project = await use_case.execute(workspace_id, id)
    return ProjectDetailSchema.model_validate(project)


@router.put("/{id}/statuses/", operation_id="api_projects_statuses_update")
async def set_project_workflow(
    id: int,
    body: WorkflowInput,
    workspace_id: WorkspaceId,
    use_case: SetProjectWorkflowDep,
) -> ProjectDetailSchema:
    """Replace this project board's workflow with the complete list sent.

    One request covers adding, renaming, reordering and removing statuses, since
    the rules a workflow must satisfy only make sense against a finished list.
    """
    project = await use_case.execute(workspace_id, id, body.to_domain())
    return ProjectDetailSchema.model_validate(project)


@router.patch("/{id}/", operation_id="api_projects_partial_update")
async def update_project(
    id: int,
    body: ProjectUpdateInput,
    workspace_id: WorkspaceId,
    use_case: UpdateProjectDep,
) -> ProjectSchema:
    project = await use_case.execute(workspace_id, id, body.to_domain())
    return ProjectSchema.model_validate(project)


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_projects_destroy",
)
async def delete_project(
    id: int, workspace_id: WorkspaceId, use_case: DeleteProjectDep
) -> None:
    await use_case.execute(workspace_id, id)
