"""Domain entities returned by use cases.

Plain, frozen dataclasses with no dependency on SQLModel or the web schemas.
Repositories map their ORM rows to these; routes map these to response models.
Keeping them framework-free is what lets use cases stay framework-agnostic.
"""

from dataclasses import dataclass
from datetime import date, datetime

from use_cases.task_status import TaskStatus


@dataclass(frozen=True)
class User:
    id: int
    username: str
    hashed_password: str
    is_active: bool
    is_staff: bool


@dataclass(frozen=True)
class Task:
    id: int
    user_id: int
    project_id: int | None
    title: str
    description: str
    status: TaskStatus
    position: int
    due_date: date | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Project:
    id: int
    user_id: int
    name: str
    color: str | None
    position: int
    # Derived read-model value: how many tasks belong to the project.
    task_count: int
    created_at: datetime
    updated_at: datetime
