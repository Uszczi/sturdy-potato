"""Scope task position to its board column.

Task ``position`` used to be a single per-user sequence shared across every
project and status. It is now scoped to one board column — a
``(user_id, project_id, status)`` group — so each column numbers its tasks from
0 independently. This renumbers existing rows into that scheme; the sort inside
each group preserves the order tasks already had.

Revision ID: e7a1c3d5f9b2
Revises: d4e5f6a7b8c9
Create Date: 2026-08-21 00:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "e7a1c3d5f9b2"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Renumber each column group to a contiguous 0..N by the order rows already had.
# NULL project_id rows (the inbox) land in one partition per status, as intended.
_RENUMBER = """
WITH ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY user_id, project_id, status
               ORDER BY position, id
           ) - 1 AS rn
    FROM todos
)
UPDATE todos
SET position = ranked.rn
FROM ranked
WHERE todos.id = ranked.id
"""

# Collapse back to a single per-user sequence (best effort: order by the old
# columns so the relative order within each user is stable).
_FLATTEN = """
WITH ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY user_id
               ORDER BY position, id
           ) - 1 AS rn
    FROM todos
)
UPDATE todos
SET position = ranked.rn
FROM ranked
WHERE todos.id = ranked.id
"""


def upgrade() -> None:
    op.execute(_RENUMBER)


def downgrade() -> None:
    op.execute(_FLATTEN)
