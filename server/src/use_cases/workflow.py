"""The Workflow: the ordered statuses a task may occupy.

A framework-free domain type (no SQLModel, no Pydantic) so the use-case layer can
reason about statuses without importing infrastructure or the web schemas.

A workspace owns a default Workflow; every project gets its own copy when it is
created and edits it independently. The workspace's own Workflow also serves the
inbox — the board of tasks belonging to no project.

Which statuses exist is per-project, so a status key alone never tells you whether
a task is finished: ``shipped`` may be terminal in one project and not in another.
Every write therefore pairs the key with its done-ness as a ``StatusAssignment``,
which is what keeps the denormalised ``Task.is_done`` column honest (ADR-0001).
"""

import re
from dataclasses import dataclass
from typing import Any, Self

from use_cases.exceptions import InvalidWorkflow, UnknownStatus

# A workflow needs somewhere to start and somewhere to finish, hence two. The
# ceiling is arbitrary: it exists so a bad client can't paste a board no one
# could read (or scroll) into a project.
MIN_STATUSES = 2
MAX_STATUSES = 50

# Keys are opaque identifiers a task row stores, so they stay url- and
# json-friendly. The length is the domain's rule; the ``todos.status`` column and
# the request schema both size themselves from it rather than restating it.
MAX_KEY_LENGTH = 20
_KEY = re.compile(rf"^[a-z0-9][a-z0-9_-]{{0,{MAX_KEY_LENGTH - 1}}}$")
MAX_LABEL_LENGTH = 50


@dataclass(frozen=True)
class Status:
    """One entry in a Workflow.

    ``key`` is what a task row stores and never changes once created; ``label``
    is what people see and can be renamed freely, which is the whole reason the
    two are separate fields.
    """

    key: str
    label: str
    is_initial: bool = False
    is_terminal: bool = False


@dataclass(frozen=True)
class StatusAssignment:
    """A status key together with its done-ness.

    Nothing writes a task's status without going through one of these, so
    ``status`` and the denormalised ``is_done`` can't be updated apart.
    """

    key: str
    is_done: bool

    def as_changes(self) -> dict[str, Any]:
        """The two columns a status write always touches, as a changes mapping."""
        return {"status": self.key, "is_done": self.is_done}


@dataclass(frozen=True)
class Workflow:
    """An ordered, validated list of the statuses a task may occupy.

    Order is the tuple's own order — it is what the board renders left to right,
    so there is no separate position field that could disagree with it.
    """

    statuses: tuple[Status, ...]

    def __post_init__(self) -> None:
        if not MIN_STATUSES <= len(self.statuses) <= MAX_STATUSES:
            raise InvalidWorkflow(
                f"A workflow needs between {MIN_STATUSES} and {MAX_STATUSES} statuses."
            )
        if len(set(self.keys)) != len(self.statuses):
            raise InvalidWorkflow("Status keys must be unique within a workflow.")
        for status in self.statuses:
            if not _KEY.match(status.key):
                raise InvalidWorkflow(f"'{status.key}' is not a valid status key.")
            if not status.label.strip() or len(status.label) > MAX_LABEL_LENGTH:
                raise InvalidWorkflow(
                    f"Status '{status.key}' needs a label of at most "
                    f"{MAX_LABEL_LENGTH} characters."
                )
        if len([s for s in self.statuses if s.is_initial]) != 1:
            raise InvalidWorkflow("A workflow needs exactly one initial status.")
        if not any(s.is_terminal for s in self.statuses):
            raise InvalidWorkflow("A workflow needs at least one terminal status.")
        # Otherwise every new task would be born finished.
        if any(s.is_initial and s.is_terminal for s in self.statuses):
            raise InvalidWorkflow("The initial status cannot also be terminal.")

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(status.key for status in self.statuses)

    @property
    def initial(self) -> Status:
        """The status a new task starts in. Exactly one exists, by validation."""
        return next(status for status in self.statuses if status.is_initial)

    @property
    def first_terminal(self) -> Status:
        """The earliest finished status: where work lands when it is completed."""
        return next(status for status in self.statuses if status.is_terminal)

    def has(self, key: str) -> bool:
        return key in self.keys

    def is_terminal(self, key: str) -> bool:
        return any(s.key == key and s.is_terminal for s in self.statuses)

    def assign(self, key: str) -> StatusAssignment:
        """Pair ``key`` with its done-ness here, rejecting statuses we don't have."""
        if not self.has(key):
            raise UnknownStatus(f"'{key}' is not a status of this workflow.")
        return StatusAssignment(key=key, is_done=self.is_terminal(key))

    def assign_initial(self) -> StatusAssignment:
        return self.assign(self.initial.key)

    def adopt(self, key: str, *, is_done: bool) -> StatusAssignment:
        """Place a task arriving from another workflow.

        A key this workflow also uses is kept (its done-ness is re-read from
        here, since the same key can mean different things in two projects).
        Anything else maps by intent: finished work lands in the first terminal
        status, unfinished work in the initial one — so a move between projects
        never silently un-completes a task.
        """
        if self.has(key):
            return self.assign(key)
        return self.assign(self.first_terminal.key if is_done else self.initial.key)

    @classmethod
    def from_dicts(cls, entries: list[dict[str, Any]]) -> Self:
        """Rebuild from the stored JSON form, validating as if freshly authored."""
        return cls(
            tuple(
                Status(
                    key=entry["key"],
                    label=entry["label"],
                    is_initial=entry["is_initial"],
                    is_terminal=entry["is_terminal"],
                )
                for entry in entries
            )
        )

    def to_dicts(self) -> list[dict[str, Any]]:
        return [
            {
                "key": status.key,
                "label": status.label,
                "is_initial": status.is_initial,
                "is_terminal": status.is_terminal,
            }
            for status in self.statuses
        ]


# What a workspace (and so every project created under it) starts with.
DEFAULT_WORKFLOW = Workflow(
    (
        Status(key="open", label="Open", is_initial=True),
        Status(key="done", label="Done", is_terminal=True),
    )
)
