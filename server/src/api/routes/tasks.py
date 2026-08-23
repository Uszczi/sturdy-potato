from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from api.dependencies import (
    CountTasksDep,
    CreateTaskDep,
    DeleteTaskDep,
    GetTaskDep,
    ListOpenTasksDep,
    ListTasksDep,
    MoveTaskDep,
    UpdateTaskDep,
    ViewTasksDep,
)
from auth import WorkspaceId
from schemas.task import (
    TaskCountSchema,
    TaskCreateInput,
    TaskMoveInput,
    TaskSchema,
    TaskUpdateInput,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/tasks", tags=["tasks"])


@router.get("/", operation_id="api_tasks_list")
async def list_tasks(
    workspace_id: WorkspaceId, use_case: ListTasksDep
) -> list[TaskSchema]:
    tasks = await use_case.execute(workspace_id)
    return [TaskSchema.model_validate(task) for task in tasks]


@router.post("/", status_code=status.HTTP_201_CREATED, operation_id="api_tasks_create")
async def create_task(
    body: TaskCreateInput, workspace_id: WorkspaceId, use_case: CreateTaskDep
) -> TaskSchema:
    task = await use_case.execute(workspace_id, body.to_domain())
    return TaskSchema.model_validate(task)


@router.get("/view/", operation_id="api_tasks_view_list")
async def view_tasks(
    workspace_id: WorkspaceId,
    use_case: ViewTasksDep,
    view: Annotated[Literal["inbox", "today", "upcoming", "all"], Query()] = "inbox",
    project: Annotated[int | None, Query()] = None,
    # IANA name (e.g. "Europe/Warsaw") so "today"/"upcoming" resolve against the
    # client's local day, not the server's. Defaults to UTC when omitted.
    tz: Annotated[str, Query()] = "UTC",
) -> list[TaskSchema]:
    tasks = await use_case.execute(workspace_id, view=view, project_id=project, tz=tz)
    return [TaskSchema.model_validate(task) for task in tasks]


@router.get("/open/", operation_id="api_tasks_open_list")
async def open_tasks(
    workspace_id: WorkspaceId,
    use_case: ListOpenTasksDep,
    limit: Annotated[int | None, Query(ge=0)] = None,
) -> list[TaskSchema]:
    tasks = await use_case.execute(workspace_id, limit=limit)
    return [TaskSchema.model_validate(task) for task in tasks]


@router.get("/count/", operation_id="api_tasks_count_retrieve")
async def count_tasks(
    workspace_id: WorkspaceId,
    use_case: CountTasksDep,
    # Counts span every board in the workspace, and boards can disagree on which
    # status keys mean "finished", so the filter is done-ness, not a status.
    done: Annotated[bool | None, Query()] = None,
) -> TaskCountSchema:
    total = await use_case.execute(workspace_id, done=done)
    return TaskCountSchema(count=total)


@router.post(
    "/{id}/move/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_tasks_move_create",
)
async def move_task(
    id: int, body: TaskMoveInput, workspace_id: WorkspaceId, use_case: MoveTaskDep
) -> None:
    await use_case.execute(workspace_id, id, body.status, body.position)


@router.get("/{id}/", operation_id="api_tasks_retrieve")
async def retrieve_task(
    id: int, workspace_id: WorkspaceId, use_case: GetTaskDep
) -> TaskSchema:
    task = await use_case.execute(workspace_id, id)
    return TaskSchema.model_validate(task)


@router.patch("/{id}/", operation_id="api_tasks_partial_update")
async def update_task(
    id: int,
    body: TaskUpdateInput,
    workspace_id: WorkspaceId,
    use_case: UpdateTaskDep,
) -> TaskSchema:
    task = await use_case.execute(workspace_id, id, body.to_domain())
    return TaskSchema.model_validate(task)


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_tasks_destroy",
)
async def delete_task(
    id: int, workspace_id: WorkspaceId, use_case: DeleteTaskDep
) -> None:
    await use_case.execute(workspace_id, id)
