"""Input data structures use cases accept.

These are the framework-free equivalents of the Pydantic request models. Routes
translate validated request bodies into these before calling a use case, so the
use-case layer never imports ``schemas`` (a web concern).
"""

from dataclasses import dataclass, fields
from datetime import date
from enum import Enum
from typing import Any


class _Unset(Enum):
    """Singleton sentinel for "field not provided" in partial updates.

    An Enum gives us a distinct, typeable singleton so ``str | Unset`` narrows
    correctly under strict typing (unlike a bare ``object()``).
    """

    token = 0


UNSET = _Unset.token
type Unset = _Unset


@dataclass(frozen=True)
class IssuedTokens:
    access: str
    refresh: str


@dataclass(frozen=True)
class TaskCreateData:
    title: str
    description: str
    completed: bool
    project_id: int | None
    due_date: date | None


@dataclass(frozen=True)
class TaskUpdateData:
    title: str | Unset = UNSET
    description: str | Unset = UNSET
    completed: bool | Unset = UNSET
    project_id: int | None | Unset = UNSET
    due_date: date | None | Unset = UNSET

    def to_changes(self) -> dict[str, Any]:
        """Only the fields the caller actually set (mirrors ``exclude_unset``)."""
        return {
            field.name: value
            for field in fields(self)
            if (value := getattr(self, field.name)) is not UNSET
        }


@dataclass(frozen=True)
class ProjectCreateData:
    name: str
    color: str | None


@dataclass(frozen=True)
class ProjectUpdateData:
    name: str | Unset = UNSET
    color: str | None | Unset = UNSET

    def to_changes(self) -> dict[str, Any]:
        return {
            field.name: value
            for field in fields(self)
            if (value := getattr(self, field.name)) is not UNSET
        }
