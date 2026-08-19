from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


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


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_project_name_per_user"),
        # Every project query filters by user then orders by position.
        Index("ix_project_user_position", "user_id", "position"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    # Optional accent colour as a "#rrggbb" hex string; null falls back to the
    # theme's primary colour in the UI.
    color: str | None = Field(default=None, max_length=7)
    position: int = 0
    created_at: datetime = _created_at_field()
    updated_at: datetime = _updated_at_field()


class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    __table_args__ = (
        # Matches the repository access patterns: list-all (user, position) and
        # the open-tasks view (user, completed, position).
        Index("ix_todo_user_position", "user_id", "position"),
        Index("ix_todo_user_completed_position", "user_id", "completed", "position"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: int | None = Field(default=None, foreign_key="projects.id")
    title: str = Field(max_length=200)
    description: str = ""
    completed: bool = False
    position: int = 0
    due_date: date | None = None
    created_at: datetime = _created_at_field()
    updated_at: datetime = _updated_at_field()
