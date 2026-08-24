import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    add_member,
    auth_headers,
    create_project,
    create_task,
    create_user,
    create_user_with_workspace,
)


async def test_list_returns_only_the_workspaces_projects_with_task_count(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, name="Visible")
    await create_task(session, workspace, project=project)
    _other, other_workspace = await create_user_with_workspace(session)
    await create_project(session, other_workspace, name="Hidden")

    response = await client.get("/api/projects/", headers=auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Visible"
    assert body[0]["task_count"] == 1


async def test_list_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/projects/")

    assert response.status_code == 401


async def test_create_project(client: AsyncClient, session: AsyncSession) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.post(
        "/api/projects/",
        headers=auth_headers(user),
        json={"name": "Roadmap"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Roadmap"
    assert response.json()["task_count"] == 0


async def test_create_project_rejects_duplicate_name(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_project(session, workspace, name="Roadmap")

    response = await client.post(
        "/api/projects/",
        headers=auth_headers(user),
        json={"name": "Roadmap"},
    )

    assert response.status_code == 400


async def test_retrieve_project(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, name="Launch")
    await create_task(session, workspace, project=project)

    response = await client.get(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Launch"
    assert response.json()["task_count"] == 1


async def test_retrieve_missing_project_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.get("/api/projects/999/", headers=auth_headers(user))

    assert response.status_code == 404


async def test_create_project_with_color(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.post(
        "/api/projects/",
        headers=auth_headers(user),
        json={"name": "Roadmap", "color": "#6366F1"},
    )

    assert response.status_code == 201
    # Hex colours are normalised to lower case.
    assert response.json()["color"] == "#6366f1"


@pytest.mark.parametrize("color", ["blue", 123])
async def test_create_project_rejects_invalid_color(
    client: AsyncClient, session: AsyncSession, color: object
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.post(
        "/api/projects/",
        headers=auth_headers(user),
        json={"name": "Roadmap", "color": color},
    )

    assert response.status_code == 422


async def test_update_project_color(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, color="#f43f5e")

    response = await client.patch(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
        json={"color": "#10b981"},
    )

    assert response.status_code == 200
    assert response.json()["color"] == "#10b981"


async def test_clear_project_color(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, color="#f43f5e")

    response = await client.patch(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
        json={"color": None},
    )

    assert response.status_code == 200
    assert response.json()["color"] is None


async def test_rename_project(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, name="Old")

    response = await client.patch(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
        json={"name": "New"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New"


async def test_rename_project_rejects_duplicate_name(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_project(session, workspace, name="Taken")
    project = await create_project(session, workspace, name="Free")

    response = await client.patch(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
        json={"name": "Taken"},
    )

    assert response.status_code == 400


async def test_update_missing_project_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.patch(
        "/api/projects/999/",
        headers=auth_headers(user),
        json={"name": "X"},
    )

    assert response.status_code == 404


async def test_reorder_projects(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    first = await create_project(session, workspace, name="First", position=0)
    second = await create_project(session, workspace, name="Second", position=1)

    response = await client.post(
        "/api/projects/reorder/",
        headers=auth_headers(user),
        json={"order": [second.id, first.id]},
    )

    assert response.status_code == 204
    listed = await client.get("/api/projects/", headers=auth_headers(user))
    assert [project["id"] for project in listed.json()] == [second.id, first.id]


async def test_reorder_with_an_empty_order_is_a_noop(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.post(
        "/api/projects/reorder/",
        headers=auth_headers(user),
        json={"order": []},
    )

    assert response.status_code == 204


async def test_reorder_rejects_another_workspaces_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    _other, other_workspace = await create_user_with_workspace(session)
    foreign = await create_project(session, other_workspace)

    response = await client.post(
        "/api/projects/reorder/",
        headers=auth_headers(user),
        json={"order": [project.id, foreign.id]},
    )

    assert response.status_code == 400


async def test_deleting_a_project_deletes_its_tasks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    task = await create_task(session, workspace, project=project)
    inbox_task = await create_task(session, workspace)

    response = await client.delete(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
    )

    assert response.status_code == 204
    retrieved = await client.get(f"/api/tasks/{task.id}/", headers=auth_headers(user))
    assert retrieved.status_code == 404
    # Only the project's own tasks go; the inbox is untouched.
    survivor = await client.get(
        f"/api/tasks/{inbox_task.id}/",
        headers=auth_headers(user),
    )
    assert survivor.status_code == 200


async def test_delete_missing_project_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.delete("/api/projects/999/", headers=auth_headers(user))

    assert response.status_code == 404


async def test_non_member_cannot_retrieve_a_projects_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    _owner, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, name="Private")
    intruder = await create_user(session)

    response = await client.get(
        f"/api/projects/{project.id}/",
        headers=auth_headers(intruder, workspace),
    )

    assert response.status_code == 404


async def test_non_member_cannot_update_a_projects_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    _owner, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, name="Private")
    intruder = await create_user(session)

    response = await client.patch(
        f"/api/projects/{project.id}/",
        headers=auth_headers(intruder, workspace),
        json={"name": "Hijacked"},
    )

    assert response.status_code == 404


async def test_non_member_cannot_delete_a_projects_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace, name="Private")
    intruder = await create_user(session)

    response = await client.delete(
        f"/api/projects/{project.id}/",
        headers=auth_headers(intruder, workspace),
    )

    assert response.status_code == 404
    still_there = await client.get(
        f"/api/projects/{project.id}/",
        headers=auth_headers(owner),
    )
    assert still_there.status_code == 200


async def test_a_member_shares_the_workspaces_projects(
    client: AsyncClient, session: AsyncSession
) -> None:
    _owner, workspace = await create_user_with_workspace(session)
    await create_project(session, workspace, name="Shared")
    teammate = await create_user(session)
    await add_member(session, workspace, teammate)

    response = await client.get(
        "/api/projects/", headers=auth_headers(teammate, workspace)
    )

    assert response.status_code == 200
    assert [project["name"] for project in response.json()] == ["Shared"]
