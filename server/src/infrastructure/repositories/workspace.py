from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from infrastructure.models import Workspace, WorkspaceMembership
from use_cases.entities import Workspace as WorkspaceEntity
from use_cases.workflow import Workflow

# Personal workspace sorts first, then oldest-created, so a user's default lands
# at the top of their list.
_ORDER = (col(Workspace.is_personal).desc(), col(Workspace.id))


def _to_entity(workspace: Workspace) -> WorkspaceEntity:
    assert workspace.id is not None
    return WorkspaceEntity(
        id=workspace.id,
        name=workspace.name,
        workflow=Workflow.from_dicts(workspace.workflow),
        is_personal=workspace.is_personal,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


class WorkspaceRepository:
    """SQLAlchemy-backed implementation of the ``WorkspaceRepository`` port.

    Writes flush but do not commit; the Unit of Work owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, owner_id: int, name: str, *, is_personal: bool = False
    ) -> WorkspaceEntity:
        workspace = Workspace(name=name, is_personal=is_personal)
        self._session.add(workspace)
        # Flush so the workspace gets its primary key before the membership row
        # references it, all inside the caller's transaction.
        await self._session.flush()
        assert workspace.id is not None
        self._session.add(
            WorkspaceMembership(
                workspace_id=workspace.id, user_id=owner_id, role="owner"
            )
        )
        await self._session.flush()
        return _to_entity(workspace)

    async def _get_orm(self, workspace_id: int) -> Workspace | None:
        workspace: Workspace | None = await self._session.scalar(
            select(Workspace).where(col(Workspace.id) == workspace_id)
        )
        return workspace

    async def get(self, workspace_id: int) -> WorkspaceEntity | None:
        workspace = await self._get_orm(workspace_id)
        return _to_entity(workspace) if workspace is not None else None

    async def set_workflow(
        self, workspace_id: int, workflow: Workflow
    ) -> WorkspaceEntity | None:
        workspace = await self._get_orm(workspace_id)
        if workspace is None:
            return None
        workspace.workflow = workflow.to_dicts()
        self._session.add(workspace)
        await self._session.flush()
        return _to_entity(workspace)

    async def list_for_user(self, user_id: int) -> list[WorkspaceEntity]:
        statement = (
            select(Workspace)
            .join(
                WorkspaceMembership,
                col(WorkspaceMembership.workspace_id) == col(Workspace.id),
            )
            .where(col(WorkspaceMembership.user_id) == user_id)
            .order_by(*_ORDER)
        )
        return [_to_entity(w) for w in await self._session.scalars(statement)]

    async def get_personal(self, user_id: int) -> WorkspaceEntity | None:
        """The user's personal workspace — what a request without a chosen one gets.

        Registration mints exactly one per user; ordering by id keeps the answer
        stable if a fixture (or a migration) ever left more than one behind.
        """
        statement = (
            select(Workspace)
            .join(
                WorkspaceMembership,
                col(WorkspaceMembership.workspace_id) == col(Workspace.id),
            )
            .where(
                col(WorkspaceMembership.user_id) == user_id,
                col(Workspace.is_personal).is_(True),
            )
            .order_by(col(Workspace.id))
        )
        workspace = (await self._session.scalars(statement)).first()
        return _to_entity(workspace) if workspace is not None else None

    async def is_member(self, user_id: int, workspace_id: int) -> bool:
        statement = select(col(WorkspaceMembership.id)).where(
            col(WorkspaceMembership.user_id) == user_id,
            col(WorkspaceMembership.workspace_id) == workspace_id,
        )
        return (await self._session.scalar(statement)) is not None
