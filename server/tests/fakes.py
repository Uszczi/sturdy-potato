"""In-memory repository fakes implementing the use-case ports.

These let use cases be exercised with no FastAPI and no database, which is the
whole point of typing use cases against ports instead of the SQLAlchemy
repositories. They keep only the behaviour the use cases rely on.
"""

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from use_cases.dtos import ProjectCreateData, TaskCreateData
from use_cases.entities import Project, Task, User
from use_cases.exceptions import InvalidToken


def _now() -> datetime:
    return datetime.now(UTC)


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self._users = {u.username: u for u in users or []}

    async def get_by_username(self, username: str) -> User | None:
        return self._users.get(username)


class FakePasswordHasher:
    """Stores hashes as ``"hash:<password>"`` so verify is a plain comparison."""

    def hash(self, password: str) -> str:
        return f"hash:{password}"

    async def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == self.hash(password)


class FakeTokenIssuer:
    def access_token(self, user_id: int) -> str:
        return f"access:{user_id}"

    def refresh_token(self, user_id: int) -> str:
        return f"refresh:{user_id}"

    def user_id_from_refresh(self, token: str) -> int:
        prefix = "refresh:"
        if not token.startswith(prefix):
            raise InvalidToken()
        return int(token.removeprefix(prefix))


class FakeTaskRepository:
    def __init__(self, tasks: list[Task] | None = None) -> None:
        self._tasks: dict[int, Task] = {t.id: t for t in tasks or []}
        self._next_id = max(self._tasks, default=0) + 1

    async def get(self, user_id: int, task_id: int) -> Task | None:
        task = self._tasks.get(task_id)
        return task if task is not None and task.user_id == user_id else None

    async def create(self, user_id: int, data: TaskCreateData) -> Task:
        position = max((t.position for t in self._owned(user_id)), default=-1) + 1
        task = Task(
            id=self._next_id,
            user_id=user_id,
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            completed=data.completed,
            position=position,
            due_date=data.due_date,
            created_at=_now(),
            updated_at=_now(),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    async def update(
        self, user_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> Task | None:
        existing = await self.get(user_id, task_id)
        if existing is None:
            return None
        # Entities are frozen; a change produces a new value.
        fields = {**existing.__dict__, **changes, "updated_at": _now()}
        updated = Task(**fields)
        self._tasks[task_id] = updated
        return updated

    async def delete(self, user_id: int, task_id: int) -> bool:
        if await self.get(user_id, task_id) is None:
            return False
        del self._tasks[task_id]
        return True

    async def ordered_ids(self, user_id: int) -> list[int]:
        owned = sorted(self._owned(user_id), key=lambda t: (t.position, -t.id))
        return [t.id for t in owned]

    async def set_positions(self, user_id: int, positions: Mapping[int, int]) -> None:
        for task_id, position in positions.items():
            task = self._tasks[task_id]
            self._tasks[task_id] = Task(**{**task.__dict__, "position": position})

    def _owned(self, user_id: int) -> list[Task]:
        return [t for t in self._tasks.values() if t.user_id == user_id]


class FakeProjectRepository:
    def __init__(self, projects: list[Project] | None = None) -> None:
        self._projects: dict[int, Project] = {p.id: p for p in projects or []}
        self._next_id = max(self._projects, default=0) + 1

    async def get(self, user_id: int, project_id: int) -> Project | None:
        project = self._projects.get(project_id)
        return project if project is not None and project.user_id == user_id else None

    async def exists(self, user_id: int, project_id: int) -> bool:
        return await self.get(user_id, project_id) is not None

    async def name_exists(
        self, user_id: int, name: str, *, exclude_id: int | None = None
    ) -> bool:
        return any(
            p.user_id == user_id and p.name == name and p.id != exclude_id
            for p in self._projects.values()
        )

    async def create(self, user_id: int, data: ProjectCreateData) -> Project:
        project = Project(
            id=self._next_id,
            user_id=user_id,
            name=data.name,
            color=data.color,
            position=0,
            task_count=0,
            created_at=_now(),
            updated_at=_now(),
        )
        self._projects[project.id] = project
        self._next_id += 1
        return project
