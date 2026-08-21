from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, UniqueConstraint
from sqlmodel import Field, SQLModel

from use_cases.task_status import TaskStatus


def utcnow() -> datetime:
    return datetime.now(UTC)


def _created_at_field() -> Any:
    return Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


def _updated_at_field() -> Any:
    # Python-side onupdate keeps updated_at fresh on every UPDATE.
    return Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=utcnow),
    )


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=150)
    hashed_password: str
    is_active: bool = True
    is_staff: bool = False


class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    # True for the workspace minted for a user at registration. Lets the client
    # single out a user's default workspace without inspecting memberships.
    is_personal: bool = False
    created_at: datetime = _created_at_field()
    updated_at: datetime = _updated_at_field()


class WorkspaceMembership(SQLModel, table=True):
    __tablename__ = "workspace_memberships"
    __table_args__ = (
        # A user joins a workspace at most once.
        UniqueConstraint("workspace_id", "user_id", name="unique_membership_per_user"),
        # Listing a user's workspaces filters by user_id.
        Index("ix_membership_user", "user_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    workspace_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    # "owner" for the creator; "member" for anyone later invited.
    role: str = Field(default="member", max_length=20)
    created_at: datetime = _created_at_field()


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "name", name="unique_project_name_per_workspace"
        ),
        # Every project query filters by workspace then orders by position.
        Index("ix_project_workspace_position", "workspace_id", "position"),
    )

    id: int | None = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspaces.id")
    name: str = Field(max_length=100)
    # Optional accent colour as a "#rrggbb" hex string; null falls back to the
    # theme's primary colour in the UI.
    color: str | None = Field(default=None, max_length=7)
    position: int = 0
    created_at: datetime = _created_at_field()
    updated_at: datetime = _updated_at_field()


class Task(SQLModel, table=True):
    # The class is ``Task`` (matching the domain vocabulary), but the physical
    # table keeps its original name so no data migration is needed.
    __tablename__ = "todos"
    __table_args__ = (
        # Matches the repository access patterns: list-all (workspace, position)
        # and the open-tasks view (workspace, status, position).
        Index("ix_todo_workspace_position", "workspace_id", "position"),
        Index(
            "ix_todo_workspace_status_position",
            "workspace_id",
            "status",
            "position",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspaces.id")
    project_id: int | None = Field(default=None, foreign_key="projects.id")
    title: str = Field(max_length=200)
    description: str = ""
    # Stored as a plain string (not a DB enum) so a future per-project status
    # setting can introduce new values without a schema migration. The domain's
    # TaskStatus is the source of truth for which values are valid.
    status: str = Field(default=TaskStatus.OPEN, max_length=20)
    position: int = 0
    due_date: date | None = None
    created_at: datetime = _created_at_field()
    updated_at: datetime = _updated_at_field()


class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    __table_args__ = (
        # Comments are always read as one task's thread, oldest first.
        Index("ix_comment_task_created", "task_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    # ON DELETE CASCADE so deleting a task takes its comments with it; the DB
    # does the cleanup, so no ORM relationship is needed on the delete path.
    task_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("todos.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    # Scopes the comment to a workspace so access checks match tasks/projects;
    # a comment always shares its task's workspace.
    workspace_id: int = Field(foreign_key="workspaces.id")
    # The author. Access is by workspace, but we still record which member wrote
    # the comment (in a shared workspace this is no longer just the task owner).
    user_id: int = Field(foreign_key="users.id")
    body: str = Field(max_length=2000)
    created_at: datetime = _created_at_field()
    updated_at: datetime = _updated_at_field()
