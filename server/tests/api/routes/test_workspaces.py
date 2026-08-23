"""The workspace endpoints: listing the caller's workspaces and creating one."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    add_member,
    auth_headers,
    create_user,
    create_user_with_workspace,
    create_workspace,
)


async def test_listing_returns_the_workspaces_the_caller_belongs_to(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, personal = await create_user_with_workspace(session)
    shared = await create_workspace(session, user, name="Shared", is_personal=False)

    response = await client.get("/api/workspaces/", headers=auth_headers(user))

    assert response.status_code == 200
    # Personal first, then oldest-created, so the default lands at the top.
    assert [w["id"] for w in response.json()] == [personal.id, shared.id]
    assert [w["is_personal"] for w in response.json()] == [True, False]


async def test_listing_omits_workspaces_the_caller_is_not_a_member_of(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, personal = await create_user_with_workspace(session)
    stranger = await create_user(session)
    await create_workspace(session, stranger, name="Theirs", is_personal=False)

    response = await client.get("/api/workspaces/", headers=auth_headers(user))

    assert [w["id"] for w in response.json()] == [personal.id]


async def test_listing_includes_a_workspace_the_caller_was_added_to(
    client: AsyncClient, session: AsyncSession
) -> None:
    _, owner_workspace = await create_user_with_workspace(session)
    member = await create_user(session)
    member_personal = await create_workspace(session, member)
    await add_member(session, owner_workspace, member)

    response = await client.get("/api/workspaces/", headers=auth_headers(member))

    assert {w["id"] for w in response.json()} == {
        member_personal.id,
        owner_workspace.id,
    }


async def test_creating_a_workspace_returns_it(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.post(
        "/api/workspaces/",
        json={"name": "  Side project  "},
        headers=auth_headers(user),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Side project"
    # Only registration mints a personal workspace; user-created ones never are.
    assert body["is_personal"] is False


async def test_a_created_workspace_is_listed_for_its_creator(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    created = await client.post(
        "/api/workspaces/", json={"name": "Side project"}, headers=auth_headers(user)
    )
    listed = await client.get("/api/workspaces/", headers=auth_headers(user))

    # Creating it also makes the creator a member, so it comes back in the list.
    assert [w["id"] for w in listed.json()] == [created.json()["id"]]


async def test_creating_a_workspace_rejects_a_blank_name(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.post(
        "/api/workspaces/", json={"name": "   "}, headers=auth_headers(user)
    )

    assert response.status_code == 422


async def test_creating_a_workspace_requires_authentication(
    client: AsyncClient,
) -> None:
    response = await client.post("/api/workspaces/", json={"name": "Side project"})

    assert response.status_code == 401
