"""In-memory repository fakes implementing the use-case ports.

These let use cases be exercised with no FastAPI and no database, which is the
whole point of typing use cases against ports instead of the SQLAlchemy
repositories. They keep only the behaviour the use cases rely on.
"""

from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any

from use_cases.dtos import CommentCreateData, ProjectCreateData, TaskCreateData
from use_cases.entities import Comment, Project, Task, User, Workspace
from use_cases.exceptions import InvalidToken
from use_cases.workflow import DEFAULT_WORKFLOW, StatusAssignment, Workflow


def _now() -> datetime:
    return datetime.now(UTC)


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self._users = {u.username: u for u in users or []}
        self._next_id = max((u.id for u in self._users.values()), default=0) + 1

    async def get_by_username(self, username: str) -> User | None:
        return self._users.get(username)

    async def get_by_id(self, user_id: int) -> User | None:
        return next((u for u in self._users.values() if u.id == user_id), None)

    async def create(self, username: str, hashed_password: str) -> User:
        user = User(
            id=self._next_id,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_staff=False,
        )
        self._users[username] = user
        self._next_id += 1
        return user


class FakeWorkspaceRepository:
    def __init__(self, workspaces: list[Workspace] | None = None) -> None:
        self._workspaces: dict[int, Workspace] = {w.id: w for w in workspaces or []}
        self._next_id = max(self._workspaces, default=0) + 1
        # (workspace_id, user_id, role) membership tuples.
        self._memberships: list[tuple[int, int, str]] = []

    async def create(
        self, owner_id: int, name: str, *, is_personal: bool = False
    ) -> Workspace:
        workspace = Workspace(
            id=self._next_id,
            name=name,
            workflow=DEFAULT_WORKFLOW,
            is_personal=is_personal,
            created_at=_now(),
            updated_at=_now(),
        )
        self._workspaces[workspace.id] = workspace
        self._memberships.append((workspace.id, owner_id, "owner"))
        self._next_id += 1
        return workspace

    async def get(self, workspace_id: int) -> Workspace | None:
        return self._workspaces.get(workspace_id)

    async def set_workflow(
        self, workspace_id: int, workflow: Workflow
    ) -> Workspace | None:
        existing = self._workspaces.get(workspace_id)
        if existing is None:
            return None
        updated = Workspace(**{**existing.__dict__, "workflow": workflow})
        self._workspaces[workspace_id] = updated
        return updated

    async def list_for_user(self, user_id: int) -> list[Workspace]:
        ids = {ws_id for ws_id, uid, _ in self._memberships if uid == user_id}
        found = [self._workspaces[ws_id] for ws_id in ids]
        return sorted(found, key=lambda w: (not w.is_personal, w.id))

    async def get_personal(self, user_id: int) -> Workspace | None:
        return next(
            (w for w in await self.list_for_user(user_id) if w.is_personal), None
        )

    async def is_member(self, user_id: int, workspace_id: int) -> bool:
        return any(
            ws_id == workspace_id and uid == user_id
            for ws_id, uid, _ in self._memberships
        )

    def add_member(self, workspace_id: int, user_id: int, role: str = "member") -> None:
        """Test helper to place an existing user into a workspace."""
        self._memberships.append((workspace_id, user_id, role))


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

    def user_id_from_access(self, token: str) -> int:
        return self._user_id(token, "access:")

    def user_id_from_refresh(self, token: str) -> int:
        return self._user_id(token, "refresh:")

    def _user_id(self, token: str, prefix: str) -> int:
        if not token.startswith(prefix):
            raise InvalidToken()
        return int(token.removeprefix(prefix))


class FakeTaskRepository:
    def __init__(self, tasks: list[Task] | None = None) -> None:
        self._tasks: dict[int, Task] = {t.id: t for t in tasks or []}
        self._next_id = max(self._tasks, default=0) + 1

    async def list_all(self, workspace_id: int) -> list[Task]:
        # Group by project (inbox last, matching SQL NULLS LAST), then board
        # order within each project group.
        return sorted(
            self._owned(workspace_id),
            key=lambda t: (
                t.project_id is None,
                t.project_id or 0,
                t.is_done,
                t.position,
                -t.id,
            ),
        )

    async def list_for_view(
        self, workspace_id: int, *, view: str, project_id: int | None, today: date
    ) -> list[Task]:
        tasks = self._owned(workspace_id)
        scoped_to_one_board = project_id is not None or view == "inbox"
        if project_id is not None:
            tasks = [t for t in tasks if t.project_id == project_id]
        elif view == "inbox":
            tasks = [t for t in tasks if t.project_id is None]
        elif view == "today":
            tasks = [t for t in tasks if t.due_date == today]
        elif view == "upcoming":
            tasks = [
                t
                for t in tasks
                if t.due_date is not None and t.due_date > today and not t.is_done
            ]
        if scoped_to_one_board:
            return sorted(tasks, key=lambda t: (t.is_done, t.position, -t.id))
        return sorted(
            tasks,
            key=lambda t: (
                t.is_done,
                t.due_date is None,
                t.due_date or date.min,
                -t.created_at.timestamp(),
                -t.id,
            ),
        )

    async def list_open(self, workspace_id: int, *, limit: int | None) -> list[Task]:
        owned = sorted(
            (t for t in self._owned(workspace_id) if not t.is_done),
            key=lambda t: (t.position, -t.id),
        )
        return owned[:limit] if limit is not None else owned

    async def count(self, workspace_id: int, *, done: bool | None) -> int:
        tasks = self._owned(workspace_id)
        if done is not None:
            tasks = [t for t in tasks if t.is_done is done]
        return len(tasks)

    async def get(self, workspace_id: int, task_id: int) -> Task | None:
        task = self._tasks.get(task_id)
        return task if task is not None and task.workspace_id == workspace_id else None

    async def create(
        self, workspace_id: int, data: TaskCreateData, status: StatusAssignment
    ) -> Task:
        position = self._next_position(workspace_id, data.project_id, status.key)
        task = Task(
            id=self._next_id,
            workspace_id=workspace_id,
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            status=status.key,
            is_done=status.is_done,
            position=position,
            due_date=data.due_date,
            created_at=_now(),
            updated_at=_now(),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    async def update(
        self, workspace_id: int, task_id: int, changes: Mapping[str, Any]
    ) -> Task | None:
        existing = await self.get(workspace_id, task_id)
        if existing is None:
            return None
        # Entities are frozen; a change produces a new value.
        fields = {**existing.__dict__, **changes, "updated_at": _now()}
        # A project/status change moves the task to a new column; append it there
        # unless the caller pinned an explicit slot.
        if (
            "project_id" in changes or "status" in changes
        ) and "position" not in changes:
            fields["position"] = self._next_position(
                workspace_id, fields["project_id"], fields["status"], exclude_id=task_id
            )
        updated = Task(**fields)
        self._tasks[task_id] = updated
        return updated

    async def delete(self, workspace_id: int, task_id: int) -> bool:
        if await self.get(workspace_id, task_id) is None:
            return False
        del self._tasks[task_id]
        return True

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None:
        for task_id, position in positions.items():
            task = self._tasks[task_id]
            self._tasks[task_id] = Task(**{**task.__dict__, "position": position})

    def _next_position(
        self,
        workspace_id: int,
        project_id: int | None,
        status: str,
        *,
        exclude_id: int | None = None,
    ) -> int:
        column = [
            t
            for t in self._owned(workspace_id)
            if t.project_id == project_id and t.status == status and t.id != exclude_id
        ]
        return max((t.position for t in column), default=-1) + 1

    def _owned(self, workspace_id: int) -> list[Task]:
        return [t for t in self._tasks.values() if t.workspace_id == workspace_id]


class FakeCommentRepository:
    def __init__(self, comments: list[Comment] | None = None) -> None:
        self._comments: dict[int, Comment] = {c.id: c for c in comments or []}
        self._next_id = max(self._comments, default=0) + 1

    async def list_for_task(self, workspace_id: int, task_id: int) -> list[Comment]:
        owned = [
            c
            for c in self._comments.values()
            if c.workspace_id == workspace_id and c.task_id == task_id
        ]
        return sorted(owned, key=lambda c: (c.created_at, c.id))

    async def get(self, workspace_id: int, comment_id: int) -> Comment | None:
        comment = self._comments.get(comment_id)
        return (
            comment
            if comment is not None and comment.workspace_id == workspace_id
            else None
        )

    async def create(
        self, workspace_id: int, task_id: int, user_id: int, data: CommentCreateData
    ) -> Comment:
        comment = Comment(
            id=self._next_id,
            task_id=task_id,
            workspace_id=workspace_id,
            user_id=user_id,
            body=data.body,
            created_at=_now(),
            updated_at=_now(),
        )
        self._comments[comment.id] = comment
        self._next_id += 1
        return comment

    async def update(
        self, workspace_id: int, comment_id: int, changes: Mapping[str, Any]
    ) -> Comment | None:
        existing = await self.get(workspace_id, comment_id)
        if existing is None:
            return None
        fields = {**existing.__dict__, **changes, "updated_at": _now()}
        updated = Comment(**fields)
        self._comments[comment_id] = updated
        return updated

    async def delete(self, workspace_id: int, comment_id: int) -> bool:
        if await self.get(workspace_id, comment_id) is None:
            return False
        del self._comments[comment_id]
        return True


class FakeProjectRepository:
    def __init__(self, projects: list[Project] | None = None) -> None:
        self._projects: dict[int, Project] = {p.id: p for p in projects or []}
        self._next_id = max(self._projects, default=0) + 1

    async def list_all(self, workspace_id: int) -> list[Project]:
        return sorted(self._owned(workspace_id), key=lambda p: (p.position, p.id))

    async def get(self, workspace_id: int, project_id: int) -> Project | None:
        project = self._projects.get(project_id)
        return (
            project
            if project is not None and project.workspace_id == workspace_id
            else None
        )

    async def exists(self, workspace_id: int, project_id: int) -> bool:
        return await self.get(workspace_id, project_id) is not None

    async def name_exists(
        self, workspace_id: int, name: str, *, exclude_id: int | None = None
    ) -> bool:
        return any(
            p.workspace_id == workspace_id and p.name == name and p.id != exclude_id
            for p in self._projects.values()
        )

    async def create(
        self, workspace_id: int, data: ProjectCreateData, workflow: Workflow
    ) -> Project:
        project = Project(
            id=self._next_id,
            workspace_id=workspace_id,
            name=data.name,
            color=data.color,
            workflow=workflow,
            position=0,
            task_count=0,
            created_at=_now(),
            updated_at=_now(),
        )
        self._projects[project.id] = project
        self._next_id += 1
        return project

    async def update(
        self, workspace_id: int, project_id: int, changes: Mapping[str, Any]
    ) -> Project | None:
        existing = await self.get(workspace_id, project_id)
        if existing is None:
            return None
        fields = {**existing.__dict__, **changes, "updated_at": _now()}
        updated = Project(**fields)
        self._projects[project_id] = updated
        return updated

    async def set_workflow(
        self, workspace_id: int, project_id: int, workflow: Workflow
    ) -> Project | None:
        existing = await self.get(workspace_id, project_id)
        if existing is None:
            return None
        updated = Project(**{**existing.__dict__, "workflow": workflow})
        self._projects[project_id] = updated
        return updated

    async def delete(self, workspace_id: int, project_id: int) -> bool:
        if await self.get(workspace_id, project_id) is None:
            return False
        del self._projects[project_id]
        return True

    async def ordered_ids(self, workspace_id: int) -> list[int]:
        owned = sorted(self._owned(workspace_id), key=lambda p: (p.position, p.id))
        return [p.id for p in owned]

    async def set_positions(
        self, workspace_id: int, positions: Mapping[int, int]
    ) -> None:
        for project_id, position in positions.items():
            project = self._projects[project_id]
            self._projects[project_id] = Project(
                **{**project.__dict__, "position": position}
            )

    def _owned(self, workspace_id: int) -> list[Project]:
        return [p for p in self._projects.values() if p.workspace_id == workspace_id]
