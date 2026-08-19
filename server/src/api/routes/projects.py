from fastapi import APIRouter, status

from api.dependencies import (
    CreateProjectDep,
    DeleteProjectDep,
    GetProjectDep,
    ListProjectsDep,
    ReorderProjectsDep,
    UpdateProjectDep,
)
from auth import CurrentUserId
from schemas.order import ReorderInput
from schemas.project import ProjectCreateInput, ProjectSchema, ProjectUpdateInput

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", operation_id="api_projects_list")
async def list_projects(
    user_id: CurrentUserId, use_case: ListProjectsDep
) -> list[ProjectSchema]:
    return await use_case.execute(user_id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, operation_id="api_projects_create"
)
async def create_project(
    body: ProjectCreateInput, user_id: CurrentUserId, use_case: CreateProjectDep
) -> ProjectSchema:
    return await use_case.execute(user_id, body)


@router.post(
    "/reorder/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_projects_reorder_create",
)
async def reorder_projects(
    body: ReorderInput, user_id: CurrentUserId, use_case: ReorderProjectsDep
) -> None:
    await use_case.execute(user_id, body.order)


@router.get("/{id}/", operation_id="api_projects_retrieve")
async def retrieve_project(
    id: int, user_id: CurrentUserId, use_case: GetProjectDep
) -> ProjectSchema:
    return await use_case.execute(user_id, id)


@router.patch("/{id}/", operation_id="api_projects_partial_update")
async def update_project(
    id: int,
    body: ProjectUpdateInput,
    user_id: CurrentUserId,
    use_case: UpdateProjectDep,
) -> ProjectSchema:
    return await use_case.execute(user_id, id, body)


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_projects_destroy",
)
async def delete_project(
    id: int, user_id: CurrentUserId, use_case: DeleteProjectDep
) -> None:
    await use_case.execute(user_id, id)
