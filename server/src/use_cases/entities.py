"""Domain entities returned by use cases.

Plain, frozen dataclasses with no dependency on SQLModel or the web schemas.
Repositories map their ORM rows to these; routes map these to response models.
Keeping them framework-free is what lets use cases stay framework-agnostic.
"""

from dataclasses import dataclass
from datetime import date, datetime

from use_cases.workflow import Workflow


@dataclass(frozen=True)
class User:
    id: int
    username: str
    hashed_password: str
    is_active: bool
    is_staff: bool


@dataclass(frozen=True)
class Workspace:
    id: int
    name: str
    # The default Workflow new projects are copied from, and the one the inbox
    # (tasks belonging to no project) is rendered with.
    workflow: Workflow
    # True for the workspace auto-created for a user at registration; the client
    # picks this one as the default when no other is selected.
    is_personal: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Task:
    id: int
    workspace_id: int
    project_id: int | None
    title: str
    description: str
    # The key of a status in the owning board's Workflow. Which statuses exist
    # is per-project, so the key alone doesn't say whether the task is finished:
    # is_done carries that (ADR-0001).
    status: str
    is_done: bool
    position: int
    due_date: date | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Comment:
    id: int
    task_id: int
    workspace_id: int
    # The member who authored the comment.
    user_id: int
    body: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Project:
    id: int
    workspace_id: int
    name: str
    color: str | None
    # Copied from the workspace's default at creation, then edited independently.
    workflow: Workflow
    position: int
    # Derived read-model value: how many tasks belong to the project.
    task_count: int
    created_at: datetime
    updated_at: datetime
