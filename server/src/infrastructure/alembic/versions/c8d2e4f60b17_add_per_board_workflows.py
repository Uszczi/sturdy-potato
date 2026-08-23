"""Give every board its own workflow, and denormalise task done-ness.

Statuses used to be a fixed ``open``/``done`` pair shared by everything. They are
now per-board: a workspace owns a default workflow (which the inbox renders and
new projects copy), and each project owns its own. Since which statuses count as
finished is now per-board, ``todos.is_done`` carries that answer so the
workspace-wide "still open" reads stay a single indexed predicate (ADR-0001).

Existing rows are already valid under the new scheme: every board starts on the
``open``/``done`` workflow, which is exactly what their tasks already store, so
no task's ``status`` changes here.

Revision ID: c8d2e4f60b17
Revises: a1b2c3d4e5f6
Create Date: 2026-08-23 00:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "c8d2e4f60b17"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Spelled out rather than imported from ``use_cases.workflow``: a migration is a
# snapshot of what the schema looked like at this point, and must not change
# meaning when the domain's default later does.
_DEFAULT_WORKFLOW = (
    '[{"key": "open", "label": "Open", "is_initial": true, "is_terminal": false}, '
    '{"key": "done", "label": "Done", "is_initial": false, "is_terminal": true}]'
)


def upgrade() -> None:
    # Add nullable, backfill, then pin down: an existing table can't take a
    # NOT NULL column without a value for the rows already in it.
    for table in ("workspaces", "projects"):
        op.add_column(table, sa.Column("workflow", sa.JSON(), nullable=True))
        op.execute(f"UPDATE {table} SET workflow = '{_DEFAULT_WORKFLOW}'::json")  # noqa: S608
        op.alter_column(table, "workflow", nullable=False)

    op.add_column("todos", sa.Column("is_done", sa.Boolean(), nullable=True))
    # Under the old fixed workflow, "done" was the one terminal status.
    op.execute("UPDATE todos SET is_done = (status = 'done')")
    op.alter_column("todos", "is_done", nullable=False)
    op.create_index(
        "ix_todo_workspace_done_position",
        "todos",
        ["workspace_id", "is_done", "position"],
    )


def downgrade() -> None:
    op.drop_index("ix_todo_workspace_done_position", table_name="todos")
    op.drop_column("todos", "is_done")
    op.drop_column("projects", "workflow")
    op.drop_column("workspaces", "workflow")
