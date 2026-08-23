"""The FastMCP server and its task tools.

Each tool is a thin adapter: translate arguments into the use-case layer's
framework-free DTOs, run the use case inside an :func:`acting_context` (which
supplies the transaction, caller and workspace from request headers), and
serialize the resulting entity. The business logic itself lives in ``server``'s
``use_cases`` package and is shared verbatim with the REST API.
"""

from collections.abc import Awaitable, Callable
from datetime import date
from functools import wraps
from typing import ParamSpec, TypeVar

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from use_cases import tasks as task_use_cases
from use_cases.dtos import UNSET, TaskCreateData, TaskUpdateData, Unset
from use_cases.exceptions import UseCaseError

from potato_mcp.context import acting_context
from potato_mcp.serialization import task_to_dict

mcp: FastMCP = FastMCP("sturdy-potato-tasks")

_P = ParamSpec("_P")
_R = TypeVar("_R")


def _tool(
    fn: Callable[_P, Awaitable[_R]],
) -> Callable[_P, Awaitable[_R]]:
    """Register a tool, surfacing domain errors as clean MCP tool errors.

    Domain failures (invalid token, unknown workspace/task, conflicts) carry a
    caller-safe ``detail``; re-raise them as ``ToolError`` so the message reaches
    the client instead of a 500-style internal error.
    """

    @wraps(fn)
    async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        try:
            return await fn(*args, **kwargs)
        except UseCaseError as exc:
            raise ToolError(exc.detail) from exc

    return mcp.tool(wrapper)


@_tool
async def list_tasks() -> list[dict[str, object]]:
    """List every task in the active workspace, in board order."""
    async with acting_context() as ctx:
        tasks = await task_use_cases.ListTasks(ctx.uow.tasks).execute(ctx.workspace_id)
        return [task_to_dict(task) for task in tasks]


@_tool
async def get_task(task_id: int) -> dict[str, object]:
    """Fetch a single task by id."""
    async with acting_context() as ctx:
        task = await task_use_cases.GetTask(ctx.uow.tasks).execute(
            ctx.workspace_id, task_id
        )
        return task_to_dict(task)


@_tool
async def create_task(
    title: str,
    description: str = "",
    status: str | None = None,
    project_id: int | None = None,
    due_date: date | None = None,
) -> dict[str, object]:
    """Create a task. ``project_id``, if given, must belong to the workspace.

    ``status`` is a status key from the target board's workflow (the project's,
    or the workspace's for a task with no project); omit it to start the task in
    whichever status that board begins with.
    """
    data = TaskCreateData(
        title=title,
        description=description,
        status=status,
        project_id=project_id,
        due_date=due_date,
    )
    async with acting_context() as ctx:
        task = await task_use_cases.CreateTask(
            ctx.uow.tasks, ctx.uow.projects, ctx.uow.workspaces
        ).execute(ctx.workspace_id, data)
        return task_to_dict(task)


@_tool
async def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    project_id: int | None = None,
    due_date: date | None = None,
) -> dict[str, object]:
    """Update the given fields of a task; omitted (``None``) fields are left as-is.

    Note: because ``None`` means "leave unchanged", this prototype tool cannot
    clear a nullable field (``project_id``/``due_date``) back to null. Use
    ``move_task`` for status/position changes on the board.
    """

    def _set[T](value: T | None) -> T | Unset:
        return UNSET if value is None else value

    data = TaskUpdateData(
        title=_set(title),
        description=_set(description),
        status=_set(status),
        project_id=_set(project_id),
        due_date=_set(due_date),
    )
    async with acting_context() as ctx:
        task = await task_use_cases.UpdateTask(
            ctx.uow.tasks, ctx.uow.projects, ctx.uow.workspaces
        ).execute(ctx.workspace_id, task_id, data)
        return task_to_dict(task)


@_tool
async def delete_task(task_id: int) -> dict[str, object]:
    """Delete a task (and its comments). Returns the deleted id."""
    async with acting_context() as ctx:
        await task_use_cases.DeleteTask(ctx.uow.tasks).execute(
            ctx.workspace_id, task_id
        )
        return {"deleted": task_id}


@_tool
async def move_task(task_id: int, status: str, position: int) -> dict[str, object]:
    """Move a task to a status column and a 0-based slot within it.

    ``status`` must be a status key the task's own board offers.
    """
    async with acting_context() as ctx:
        await task_use_cases.MoveTask(
            ctx.uow.tasks, ctx.uow.projects, ctx.uow.workspaces
        ).execute(ctx.workspace_id, task_id, status, position)
        task = await task_use_cases.GetTask(ctx.uow.tasks).execute(
            ctx.workspace_id, task_id
        )
        return task_to_dict(task)
