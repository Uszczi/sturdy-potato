"""Repository interfaces (ports) the use cases depend on.

Use cases are typed against these Protocols, not the concrete SQLAlchemy
repositories. That inverts the dependency: ``infrastructure`` implements ports
defined here, so the use-case layer never imports ``infrastructure``. It also
lets tests substitute in-memory fakes without a database.
"""

from collections.abc import Mapping
from datetime import date
from typing import Any, Protocol

from use_cases.dtos import CommentCreateData, ProjectCreateData, TaskCreateData
from use_cases.entities import Comment, Project, Task, User, Workspace
from use_cases.task_status import TaskStatus


class UserRepository(Protocol):
    async def get_by_username(self, username: str) -> User | None: ...

    async def get_by_id(self, user_id: int) -> User | None: ...

    async def create(self, username: str, hashed_password: str) -> User: ...


class WorkspaceRepository(Protocol):
    # Creates the workspace and an owner membership for ``owner_id`` together.
    async def create(
        self, owner_id: int, name: str, *, is_personal: bool = False
    ) -> Workspace: ...

    async def list_for_user(self, user_id: int) -> list[Workspace]: ...

    async def is_member(self, user_id: int, workspace_id: int) -> bool: ...


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
    async def list_all(self, workspace_id: int) -> list[Task]: ...

    async def list_for_view(
        self, workspace_id: int, *, view: str, project_id: int | None, today: date
    ) -> list[Task]: ...

    async def list_open(
        self, workspace_id: int, *, limit: int | None
    ) -> list[Task]: ...

    async def count(self, workspace_id: int, *, status: TaskStatus | None) -> int: ...

    async def get(self, workspace_id: int, task_id: int) -> Task | None: ...

    async def create(self, workspace_id: int, data: TaskCreateData) -> Task: ...

    async def update(
        self, workspace_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> Task | None: ...

    async def delete(self, workspace_id: int, task_id: int) -> bool: ...

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None: ...


class CommentRepository(Protocol):
    async def list_for_task(self, workspace_id: int, task_id: int) -> list[Comment]: ...

    async def get(self, workspace_id: int, comment_id: int) -> Comment | None: ...

    async def create(
        self, workspace_id: int, task_id: int, user_id: int, data: CommentCreateData
    ) -> Comment: ...

    async def update(
        self, workspace_id: int, comment_id: int, changes: Mapping[str, Any]
    ) -> Comment | None: ...

    async def delete(self, workspace_id: int, comment_id: int) -> bool: ...


class ProjectRepository(Protocol):
    async def list_all(self, workspace_id: int) -> list[Project]: ...

    async def get(self, workspace_id: int, project_id: int) -> Project | None: ...

    async def exists(self, workspace_id: int, project_id: int) -> bool: ...

    async def name_exists(
        self, workspace_id: int, name: str, *, exclude_id: int | None = None
    ) -> bool: ...

    async def create(self, workspace_id: int, data: ProjectCreateData) -> Project: ...

    async def update(
        self, workspace_id: int, project_id: int, changes: Mapping[str, Any]
    ) -> Project | None: ...

    async def delete(self, workspace_id: int, project_id: int) -> bool: ...

    async def ordered_ids(self, workspace_id: int) -> list[int]: ...

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None: ...
