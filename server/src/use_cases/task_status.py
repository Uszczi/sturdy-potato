"""The lifecycle status of a task.

A framework-free domain type (no SQLModel, no Pydantic) so the use-case layer
can reason about status without importing infrastructure or the web schemas.

``OPEN`` and ``DONE`` are the two statuses the domain always guarantees: ``OPEN``
is the state a task starts in, ``DONE`` is the terminal/completed state. A future
per-project status setting may add statuses in between, but can never drop
``OPEN`` or ``DONE`` — they are the required baseline every project shares (see
``REQUIRED_STATUSES``). Anything that is not ``DONE`` counts as still-open work.
"""

from enum import StrEnum


class TaskStatus(StrEnum):
    OPEN = "open"
    DONE = "done"

    @property
    def is_done(self) -> bool:
        """Whether this status counts as completed/terminal."""
        return self is TaskStatus.DONE


# The statuses the domain guarantees always exist, in lifecycle order. A future
# per-project configuration may extend the available statuses but must always
# keep these two.
REQUIRED_STATUSES: tuple[TaskStatus, ...] = (TaskStatus.OPEN, TaskStatus.DONE)
