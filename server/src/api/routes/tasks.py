from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from api.dependencies import (
    CountTasksDep,
    CreateTaskDep,
    DeleteTaskDep,
    GetTaskDep,
    ListOpenTasksDep,
    ListTasksDep,
    ReorderTasksDep,
    UpdateTaskDep,
    ViewTasksDep,
)
from auth import CurrentUserId
from schemas.order import ReorderInput
from schemas.todo import (
    TaskCountSchema,
    TodoCreateInput,
    TodoSchema,
    TodoUpdateInput,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", operation_id="api_tasks_list")
async def list_tasks(
    user_id: CurrentUserId, use_case: ListTasksDep
) -> list[TodoSchema]:
    # FastAPI serializes the ORM rows via the response model; no manual parse.
    return await use_case.execute(user_id)  # type: ignore[return-value]


@router.post("/", status_code=status.HTTP_201_CREATED, operation_id="api_tasks_create")
async def create_task(
    body: TodoCreateInput, user_id: CurrentUserId, use_case: CreateTaskDep
) -> TodoSchema:
    return await use_case.execute(user_id, body)  # type: ignore[return-value]


@router.get("/view/", operation_id="api_tasks_view_list")
async def view_tasks(
    user_id: CurrentUserId,
    use_case: ViewTasksDep,
    view: Annotated[Literal["inbox", "today", "upcoming", "all"], Query()] = "inbox",
    project: Annotated[int | None, Query()] = None,
) -> list[TodoSchema]:
    return await use_case.execute(  # type: ignore[return-value]
        user_id, view=view, project_id=project
    )


@router.get("/open/", operation_id="api_tasks_open_list")
async def open_tasks(
    user_id: CurrentUserId,
    use_case: ListOpenTasksDep,
    limit: Annotated[int | None, Query(ge=0)] = None,
) -> list[TodoSchema]:
    return await use_case.execute(user_id, limit=limit)  # type: ignore[return-value]


@router.get("/count/", operation_id="api_tasks_count_retrieve")
async def count_tasks(
    user_id: CurrentUserId,
    use_case: CountTasksDep,
    completed: bool | None = None,
) -> TaskCountSchema:
    total = await use_case.execute(user_id, completed=completed)
    return TaskCountSchema(count=total)


@router.post(
    "/reorder/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_tasks_reorder_create",
)
async def reorder_tasks(
    body: ReorderInput, user_id: CurrentUserId, use_case: ReorderTasksDep
) -> None:
    await use_case.execute(user_id, body.order)


@router.get("/{id}/", operation_id="api_tasks_retrieve")
async def retrieve_task(
    id: int, user_id: CurrentUserId, use_case: GetTaskDep
) -> TodoSchema:
    return await use_case.execute(user_id, id)  # type: ignore[return-value]


@router.patch("/{id}/", operation_id="api_tasks_partial_update")
async def update_task(
    id: int,
    body: TodoUpdateInput,
    user_id: CurrentUserId,
    use_case: UpdateTaskDep,
) -> TodoSchema:
    return await use_case.execute(user_id, id, body)  # type: ignore[return-value]


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_tasks_destroy",
)
async def delete_task(
    id: int, user_id: CurrentUserId, use_case: DeleteTaskDep
) -> None:
    await use_case.execute(user_id, id)
