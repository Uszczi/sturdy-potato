from fastapi import APIRouter, HTTPException, status

from api.dependencies import ProjectRepositoryDep
from auth import CurrentUserId
from schemas.order import ReorderInput
from schemas.project import ProjectCreateInput, ProjectSchema, ProjectUpdateInput

router = APIRouter(prefix="/projects", tags=["projects"])

_name_conflict = HTTPException(
    status.HTTP_400_BAD_REQUEST, "A project with this name already exists."
)
_not_found = HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.")


@router.get("/", operation_id="api_projects_list")
async def list_projects(
    user_id: CurrentUserId, repository: ProjectRepositoryDep
) -> list[ProjectSchema]:
    return await repository.list_for_user(user_id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, operation_id="api_projects_create"
)
async def create_project(
    body: ProjectCreateInput, user_id: CurrentUserId, repository: ProjectRepositoryDep
) -> ProjectSchema:
    if await repository.name_exists(user_id, body.name):
        raise _name_conflict
    return await repository.create_for_user(user_id, body.model_dump())


@router.post(
    "/reorder/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_projects_reorder_create",
)
async def reorder_projects(
    body: ReorderInput, user_id: CurrentUserId, repository: ProjectRepositoryDep
) -> None:
    if not await repository.reorder_for_user(user_id, body.order):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Order contains projects outside this user."
        )


@router.get("/{id}/", operation_id="api_projects_retrieve")
async def retrieve_project(
    id: int, user_id: CurrentUserId, repository: ProjectRepositoryDep
) -> ProjectSchema:
    project = await repository.get_for_user(user_id, id)
    if project is None:
        raise _not_found
    return project


@router.patch("/{id}/", operation_id="api_projects_partial_update")
async def update_project(
    id: int,
    body: ProjectUpdateInput,
    user_id: CurrentUserId,
    repository: ProjectRepositoryDep,
) -> ProjectSchema:
    data = body.model_dump(exclude_unset=True)
    if "name" in data and await repository.name_exists(
        user_id, data["name"], exclude_id=id
    ):
        raise _name_conflict
    project = await repository.update(user_id, id, data)
    if project is None:
        raise _not_found
    return project


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_projects_destroy",
)
async def delete_project(
    id: int, user_id: CurrentUserId, repository: ProjectRepositoryDep
) -> None:
    if not await repository.delete(user_id, id):
        raise _not_found
