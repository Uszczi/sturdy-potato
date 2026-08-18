from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_headers, create_project, create_task, create_user


async def test_list_returns_only_the_users_projects_with_task_count(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user, name="Visible")
    await create_task(session, user, project=project)
    other = await create_user(session)
    await create_project(session, other, name="Hidden")

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
    user = await create_user(session)

    response = await client.post(
        "/api/projects/", headers=auth_headers(user), json={"name": "Roadmap"}
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Roadmap"
    assert response.json()["task_count"] == 0


async def test_create_project_rejects_duplicate_name(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    await create_project(session, user, name="Roadmap")

    response = await client.post(
        "/api/projects/", headers=auth_headers(user), json={"name": "Roadmap"}
    )

    assert response.status_code == 400


async def test_retrieve_project(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    project = await create_project(session, user, name="Launch")
    await create_task(session, user, project=project)

    response = await client.get(
        f"/api/projects/{project.id}/", headers=auth_headers(user)
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Launch"
    assert response.json()["task_count"] == 1


async def test_retrieve_missing_project_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.get("/api/projects/999/", headers=auth_headers(user))

    assert response.status_code == 404


async def test_rename_project(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    project = await create_project(session, user, name="Old")

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
    user = await create_user(session)
    await create_project(session, user, name="Taken")
    project = await create_project(session, user, name="Free")

    response = await client.patch(
        f"/api/projects/{project.id}/",
        headers=auth_headers(user),
        json={"name": "Taken"},
    )

    assert response.status_code == 400


async def test_update_missing_project_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.patch(
        "/api/projects/999/", headers=auth_headers(user), json={"name": "X"}
    )

    assert response.status_code == 404


async def test_reorder_projects(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    first = await create_project(session, user, name="First", position=0)
    second = await create_project(session, user, name="Second", position=1)

    response = await client.post(
        "/api/projects/reorder/",
        headers=auth_headers(user),
        json={"order": [second.id, first.id]},
    )

    assert response.status_code == 204
    listed = await client.get("/api/projects/", headers=auth_headers(user))
    assert [project["id"] for project in listed.json()] == [second.id, first.id]


async def test_reorder_rejects_another_users_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user)
    other = await create_user(session)
    foreign = await create_project(session, other)

    response = await client.post(
        "/api/projects/reorder/",
        headers=auth_headers(user),
        json={"order": [project.id, foreign.id]},
    )

    assert response.status_code == 400


async def test_deleting_a_project_unassigns_its_tasks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user)
    task = await create_task(session, user, project=project)

    response = await client.delete(
        f"/api/projects/{project.id}/", headers=auth_headers(user)
    )

    assert response.status_code == 204
    retrieved = await client.get(f"/api/tasks/{task.id}/", headers=auth_headers(user))
    assert retrieved.json()["project_id"] is None


async def test_delete_missing_project_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.delete("/api/projects/999/", headers=auth_headers(user))

    assert response.status_code == 404
