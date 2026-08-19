"""add project color

Revision ID: 3c1a9f2b7e04
Revises: 0af52d921cea
Create Date: 2026-08-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3c1a9f2b7e04'
down_revision: Union[str, Sequence[str], None] = '0af52d921cea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable accent colour; existing projects stay null and fall back to the
    # theme's primary colour in the UI.
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=7), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('color')
