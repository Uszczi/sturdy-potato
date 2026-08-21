"""add workspaces and scope projects/tasks/comments to them

Revision ID: a1b2c3d4e5f6
Revises: e7a1c3d5f9b2
Create Date: 2026-08-20 18:00:00.000000

Introduces ``workspaces`` and ``workspace_memberships`` and moves ownership of
projects/todos/comments from ``user_id`` to ``workspace_id``. The upgrade is
data-preserving: every existing user gets a personal workspace (with an owner
membership) and their rows are re-pointed at it before the old ``user_id``
columns are dropped.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'e7a1c3d5f9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # New tables. ``workspaces`` carries a temporary ``_seed_user_id`` so the
    # backfill can map each personal workspace back to the user it was minted
    # for; it is dropped once the data has been re-pointed.
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('is_personal', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('_seed_user_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'workspace_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'user_id', name='unique_membership_per_user'),
    )
    op.create_index('ix_membership_user', 'workspace_memberships', ['user_id'])

    # One personal workspace + owner membership per existing user.
    op.execute(
        "INSERT INTO workspaces (name, is_personal, created_at, updated_at, _seed_user_id) "
        "SELECT 'Personal', true, now(), now(), id FROM users"
    )
    op.execute(
        "INSERT INTO workspace_memberships (workspace_id, user_id, role, created_at) "
        "SELECT id, _seed_user_id, 'owner', now() FROM workspaces "
        "WHERE _seed_user_id IS NOT NULL"
    )

    # projects.workspace_id
    op.add_column('projects', sa.Column('workspace_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE projects p SET workspace_id = w.id "
        "FROM workspaces w WHERE w._seed_user_id = p.user_id"
    )
    op.alter_column('projects', 'workspace_id', nullable=False)

    # todos.workspace_id
    op.add_column('todos', sa.Column('workspace_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE todos t SET workspace_id = w.id "
        "FROM workspaces w WHERE w._seed_user_id = t.user_id"
    )
    op.alter_column('todos', 'workspace_id', nullable=False)

    # comments.workspace_id (inherited from the comment's task)
    op.add_column('comments', sa.Column('workspace_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE comments c SET workspace_id = t.workspace_id "
        "FROM todos t WHERE t.id = c.task_id"
    )
    op.alter_column('comments', 'workspace_id', nullable=False)

    # The seed helper column has served its purpose.
    op.drop_column('workspaces', '_seed_user_id')

    # Swap constraints/indexes/foreign keys from user_id to workspace_id.
    # Dropping the user_id columns cascades to the old per-user indexes and the
    # unique(user_id, name) constraint in PostgreSQL.
    op.create_foreign_key(
        'fk_projects_workspace_id', 'projects', 'workspaces', ['workspace_id'], ['id']
    )
    op.create_unique_constraint(
        'unique_project_name_per_workspace', 'projects', ['workspace_id', 'name']
    )
    op.create_index(
        'ix_project_workspace_position', 'projects', ['workspace_id', 'position']
    )
    op.drop_column('projects', 'user_id')

    op.create_foreign_key(
        'fk_todos_workspace_id', 'todos', 'workspaces', ['workspace_id'], ['id']
    )
    op.create_index(
        'ix_todo_workspace_position', 'todos', ['workspace_id', 'position']
    )
    op.create_index(
        'ix_todo_workspace_status_position',
        'todos',
        ['workspace_id', 'status', 'position'],
    )
    op.drop_column('todos', 'user_id')

    # ``comments.user_id`` is kept as the comment's author; only the new
    # workspace scoping is added.
    op.create_foreign_key(
        'fk_comments_workspace_id', 'comments', 'workspaces', ['workspace_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema.

    Best-effort reverse: user ownership is restored from each workspace's owner
    membership (comment authorship, which was dropped, is likewise restored to
    the owner).
    """
    # ``comments.user_id`` (author) was never dropped, so only remove the
    # workspace scoping added by the upgrade.
    op.drop_constraint('fk_comments_workspace_id', 'comments', type_='foreignkey')
    op.drop_column('comments', 'workspace_id')

    op.add_column('todos', sa.Column('user_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE todos t SET user_id = m.user_id "
        "FROM workspace_memberships m "
        "WHERE m.workspace_id = t.workspace_id AND m.role = 'owner'"
    )
    op.alter_column('todos', 'user_id', nullable=False)
    op.create_foreign_key('todos_user_id_fkey', 'todos', 'users', ['user_id'], ['id'])
    op.create_index('ix_todo_user_position', 'todos', ['user_id', 'position'])
    op.create_index(
        'ix_todo_user_status_position', 'todos', ['user_id', 'status', 'position']
    )
    op.drop_index('ix_todo_workspace_status_position', table_name='todos')
    op.drop_index('ix_todo_workspace_position', table_name='todos')
    op.drop_constraint('fk_todos_workspace_id', 'todos', type_='foreignkey')
    op.drop_column('todos', 'workspace_id')

    op.add_column('projects', sa.Column('user_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE projects p SET user_id = m.user_id "
        "FROM workspace_memberships m "
        "WHERE m.workspace_id = p.workspace_id AND m.role = 'owner'"
    )
    op.alter_column('projects', 'user_id', nullable=False)
    op.create_foreign_key(
        'projects_user_id_fkey', 'projects', 'users', ['user_id'], ['id']
    )
    op.create_unique_constraint(
        'unique_project_name_per_user', 'projects', ['user_id', 'name']
    )
    op.create_index('ix_project_user_position', 'projects', ['user_id', 'position'])
    op.drop_index('ix_project_workspace_position', table_name='projects')
    op.drop_constraint(
        'unique_project_name_per_workspace', 'projects', type_='unique'
    )
    op.drop_constraint('fk_projects_workspace_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'workspace_id')

    op.drop_index('ix_membership_user', table_name='workspace_memberships')
    op.drop_table('workspace_memberships')
    op.drop_table('workspaces')
