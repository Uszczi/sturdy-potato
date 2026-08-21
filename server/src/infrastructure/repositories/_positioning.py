"""Shared position helpers for the manually-ordered repositories.

Projects keep a per-workspace ``position``; tasks keep a ``position`` scoped to a
single board column, i.e. per ``(workspace, project_id, status)``. Computing the
next slot as a subquery lets the INSERT assign it atomically, so two concurrent
creates can't read the same max and collide.
"""

from sqlalchemy import ScalarSelect, func
from sqlalchemy.orm import Mapped
from sqlmodel import col, select

from infrastructure.models import Task


def next_position_subquery(
    position_col: Mapped[int], scope_col: Mapped[int], scope_id: int
) -> ScalarSelect[int]:
    """Subquery for the slot after the scope's current last row (0 when none)."""
    return (
        select(func.coalesce(func.max(position_col), -1) + 1)
        .where(scope_col == scope_id)
        .scalar_subquery()
    )


def next_task_position_subquery(
    workspace_id: int, project_id: int | None, status: str
) -> ScalarSelect[int]:
    """Subquery for the slot after a board column's current last task.

    A "column" is one ``(workspace, project_id, status)`` group — the same cards
    the kanban shows stacked together — so each column numbers its tasks from 0
    independently of every other column and project.
    """
    project_match = (
        col(Task.project_id).is_(None)
        if project_id is None
        else col(Task.project_id) == project_id
    )
    return (
        select(func.coalesce(func.max(col(Task.position)), -1) + 1)
        .where(
            col(Task.workspace_id) == workspace_id,
            project_match,
            col(Task.status) == status,
        )
        .scalar_subquery()
    )
