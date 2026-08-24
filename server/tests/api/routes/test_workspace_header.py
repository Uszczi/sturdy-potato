"""How a resource route picks the workspace it acts on.

Tasks, projects, comments and chat are not nested under a workspace id: the
caller names one in ``X-Workspace-Id``, and a request that names none acts on
the caller's personal workspace. The rules are the same for every one of those
routes, so they are exercised once here (through the task list) rather than
repeated per router.
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth import WORKSPACE_HEADER
from tests.factories import (
    auth_headers,
    create_task,
    create_user,
    create_user_with_workspace,
    create_workspace,
)


async def test_without_the_header_a_request_acts_on_the_personal_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, personal = await create_user_with_workspace(session)
    shared = await create_workspace(session, user, name="Shared", is_personal=False)
    await create_task(session, personal, title="Mine")
    await create_task(session, shared, title="Ours")

    response = await client.get("/api/tasks/", headers=auth_headers(user))

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Mine"]


async def test_the_header_selects_another_workspace_the_caller_belongs_to(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, personal = await create_user_with_workspace(session)
    shared = await create_workspace(session, user, name="Shared", is_personal=False)
    await create_task(session, personal, title="Mine")
    await create_task(session, shared, title="Ours")

    response = await client.get("/api/tasks/", headers=auth_headers(user, shared))

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Ours"]


async def test_the_header_cannot_name_a_workspace_the_caller_is_not_in(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _personal = await create_user_with_workspace(session)
    _owner, theirs = await create_user_with_workspace(session)
    await create_task(session, theirs, title="Theirs")

    response = await client.get("/api/tasks/", headers=auth_headers(user, theirs))

    # A 404 rather than a 403: membership never leaks a workspace's existence.
    assert response.status_code == 404


async def test_a_header_that_is_not_a_number_is_rejected(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _personal = await create_user_with_workspace(session)

    response = await client.get(
        "/api/tasks/", headers={**auth_headers(user), WORKSPACE_HEADER: "personal"}
    )

    assert response.status_code == 422


async def test_a_caller_with_no_personal_workspace_and_no_header_gets_a_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    # Registration always mints one, so this only happens if it was deleted;
    # the request has no workspace to fall back to.
    user = await create_user(session)
    await create_workspace(session, user, name="Shared", is_personal=False)

    response = await client.get("/api/tasks/", headers=auth_headers(user))

    assert response.status_code == 404
