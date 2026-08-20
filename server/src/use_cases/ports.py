"""Repository interfaces (ports) the use cases depend on.

Use cases are typed against these Protocols, not the concrete SQLAlchemy
repositories. That inverts the dependency: ``infrastructure`` implements ports
defined here, so the use-case layer never imports ``infrastructure``. It also
lets tests substitute in-memory fakes without a database.
"""

from collections.abc import Mapping
from datetime import date
from typing import Any, Protocol

from use_cases.dtos import ProjectCreateData, TaskCreateData
from use_cases.entities import Project, Task, User


class UserRepository(Protocol):
    async def get_by_username(self, username: str) -> User | None: ...

    async def get_by_id(self, user_id: int) -> User | None: ...

    async def create(self, username: str, hashed_password: str) -> User: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    async def verify(self, password: str, hashed_password: str) -> bool: ...


class TokenIssuer(Protocol):
    def access_token(self, user_id: int) -> str: ...

    def refresh_token(self, user_id: int) -> str: ...

    # Raises InvalidToken if the token is not a valid access token.
    def user_id_from_access(self, token: str) -> int: ...

    # Raises InvalidToken if the token is not a valid refresh token.
    def user_id_from_refresh(self, token: str) -> int: ...


class TaskRepository(Protocol):
    async def list_all(self, user_id: int) -> list[Task]: ...

    async def list_for_view(
        self, user_id: int, *, view: str, project_id: int | None, today: date
    ) -> list[Task]: ...

    async def list_open(self, user_id: int, *, limit: int | None) -> list[Task]: ...

    async def count(self, user_id: int, *, completed: bool | None) -> int: ...

    async def get(self, user_id: int, task_id: int) -> Task | None: ...

    async def create(self, user_id: int, data: TaskCreateData) -> Task: ...

    async def update(
        self, user_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> Task | None: ...

    async def delete(self, user_id: int, task_id: int) -> bool: ...

    async def ordered_ids(self, user_id: int) -> list[int]: ...

    async def set_positions(
        self, user_id: int, positions: Mapping[int, int]
    ) -> None: ...


class ProjectRepository(Protocol):
    async def list_all(self, user_id: int) -> list[Project]: ...

    async def get(self, user_id: int, project_id: int) -> Project | None: ...

    async def exists(self, user_id: int, project_id: int) -> bool: ...

    async def name_exists(
        self, user_id: int, name: str, *, exclude_id: int | None = None
    ) -> bool: ...

    async def create(self, user_id: int, data: ProjectCreateData) -> Project: ...

    async def update(
        self, user_id: int, project_id: int, changes: Mapping[str, Any]
    ) -> Project | None: ...

    async def delete(self, user_id: int, project_id: int) -> bool: ...

    async def ordered_ids(self, user_id: int) -> list[int]: ...

    async def set_positions(
        self, user_id: int, positions: Mapping[int, int]
    ) -> None: ...
