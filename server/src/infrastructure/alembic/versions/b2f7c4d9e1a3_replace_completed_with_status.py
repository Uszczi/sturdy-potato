"""replace todo.completed with a status column

Swaps the boolean ``completed`` flag for a free-form ``status`` string. Existing
rows are backfilled: completed tasks become ``'done'`` and the rest ``'open'``.
The column is a plain string (not a DB enum) so a future per-project status
setting can add values without another migration.

Revision ID: b2f7c4d9e1a3
Revises: 3c1a9f2b7e04
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f7c4d9e1a3'
down_revision: Union[str, Sequence[str], None] = '3c1a9f2b7e04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add with a server_default so the NOT NULL column is populated for existing
    # rows, then drop the default so new rows rely on the application default.
    op.add_column(
        'todos',
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
    )
    op.execute("UPDATE todos SET status = 'done' WHERE completed")
    op.create_index(
        'ix_todo_user_status_position', 'todos', ['user_id', 'status', 'position']
    )
    op.drop_index('ix_todo_user_completed_position', table_name='todos')
    op.drop_column('todos', 'completed')
    op.alter_column('todos', 'status', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'todos',
        sa.Column('completed', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE todos SET completed = true WHERE status = 'done'")
    op.create_index(
        'ix_todo_user_completed_position',
        'todos',
        ['user_id', 'completed', 'position'],
    )
    op.drop_index('ix_todo_user_status_position', table_name='todos')
    op.drop_column('todos', 'status')
    op.alter_column('todos', 'completed', server_default=None)
