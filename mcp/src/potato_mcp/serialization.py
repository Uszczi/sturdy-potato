"""Turn domain entities into JSON-friendly dicts for MCP tool results.

The use cases return frozen ``use_cases.entities`` dataclasses; MCP results must
be plain JSON, so datetimes/dates become ISO strings. Kept separate from
``server.py`` so the tool bodies stay declarative.
"""

from use_cases.entities import Task


def task_to_dict(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "workspace_id": task.workspace_id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        # Which statuses count as finished is per-board, so a caller can't read
        # done-ness off the status key alone.
        "is_done": task.is_done,
        "position": task.position,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
