from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status

from auth import CurrentUserId
from infrastructure.db import SessionDep
from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from schemas.order import ReorderInput
from schemas.todo import (
    TaskCountSchema,
    TodoCreateInput,
    TodoSchema,
    TodoUpdateInput,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

repository = TodoRepository()


async def _get_task_or_404(session: SessionDep, user_id: int, task_id: int) -> Todo:
    task = await repository.get_for_user(session, user_id, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found.")
    return task


async def _ensure_project(
    session: SessionDep, user_id: int, project_id: int | None
) -> None:
    if project_id is not None:
        project = await repository.get_project_for_user(session, user_id, project_id)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.")


@router.get("/", operation_id="api_tasks_list")
async def list_tasks(user_id: CurrentUserId, session: SessionDep) -> list[TodoSchema]:
    # FastAPI serializes the ORM rows via the response model; no manual parse.
    return await repository.list_for_user(session, user_id)  # type: ignore[return-value]


@router.post("/", status_code=status.HTTP_201_CREATED, operation_id="api_tasks_create")
async def create_task(
    body: TodoCreateInput, user_id: CurrentUserId, session: SessionDep
) -> TodoSchema:
    data = body.model_dump()
    await _ensure_project(session, user_id, data["project_id"])
    return await repository.create_for_user(session, user_id, data)  # type: ignore[return-value]


@router.get("/view/", operation_id="api_tasks_view_list")
async def view_tasks(
    user_id: CurrentUserId,
    session: SessionDep,
    view: Annotated[Literal["inbox", "today", "upcoming", "all"], Query()] = "inbox",
    project: Annotated[int | None, Query()] = None,
) -> list[TodoSchema]:
    await _ensure_project(session, user_id, project)
    return await repository.list_for_view(  # type: ignore[return-value]
        session, user_id, view=view, project_id=project
    )


@router.get("/open/", operation_id="api_tasks_open_list")
async def open_tasks(
    user_id: CurrentUserId,
    session: SessionDep,
    limit: Annotated[int | None, Query(ge=0)] = None,
) -> list[TodoSchema]:
    return await repository.list_open_for_user(session, user_id, limit=limit)  # type: ignore[return-value]


@router.get("/count/", operation_id="api_tasks_count_retrieve")
async def count_tasks(
    user_id: CurrentUserId,
    session: SessionDep,
    completed: bool | None = None,
) -> TaskCountSchema:
    total = await repository.count_for_user(session, user_id, completed=completed)
    return TaskCountSchema(count=total)


@router.post(
    "/reorder/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_tasks_reorder_create",
)
async def reorder_tasks(
    body: ReorderInput, user_id: CurrentUserId, session: SessionDep
) -> None:
    if not await repository.reorder_for_user(session, user_id, body.order):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Order contains tasks outside this user."
        )


@router.get("/{id}/", operation_id="api_tasks_retrieve")
async def retrieve_task(
    id: int, user_id: CurrentUserId, session: SessionDep
) -> TodoSchema:
    return await _get_task_or_404(session, user_id, id)  # type: ignore[return-value]


@router.patch("/{id}/", operation_id="api_tasks_partial_update")
async def update_task(
    id: int, body: TodoUpdateInput, user_id: CurrentUserId, session: SessionDep
) -> TodoSchema:
    task = await _get_task_or_404(session, user_id, id)
    data = body.model_dump(exclude_unset=True)
    if "project_id" in data:
        await _ensure_project(session, user_id, data["project_id"])
    return await repository.update(session, task, data)  # type: ignore[return-value]


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_tasks_destroy",
)
async def delete_task(id: int, user_id: CurrentUserId, session: SessionDep) -> None:
    task = await _get_task_or_404(session, user_id, id)
    await repository.delete(session, task)
