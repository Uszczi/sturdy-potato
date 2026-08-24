from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    auth_headers,
    create_comment,
    create_task,
    create_user,
    create_user_with_workspace,
)


async def test_list_returns_a_tasks_comments_oldest_first(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    with freeze_time("2024-01-01T12:00:00Z", auto_tick_seconds=1):
        await create_comment(session, workspace, user, task, body="First")
        await create_comment(session, workspace, user, task, body="Second")

    response = await client.get(
        f"/api/tasks/{task.id}/comments/",
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    assert [c["body"] for c in response.json()] == ["First", "Second"]


async def test_list_only_returns_the_given_tasks_comments(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    other_task = await create_task(session, workspace)
    await create_comment(session, workspace, user, task, body="Here")
    await create_comment(session, workspace, user, other_task, body="Elsewhere")

    response = await client.get(
        f"/api/tasks/{task.id}/comments/",
        headers=auth_headers(user),
    )

    assert [c["body"] for c in response.json()] == ["Here"]


async def test_list_for_a_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.get(
        "/api/tasks/999/comments/",
        headers=auth_headers(user),
    )

    assert response.status_code == 404


async def test_create_comment(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.post(
        f"/api/tasks/{task.id}/comments/",
        headers=auth_headers(user),
        json={"body": "  Looks good  "},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["body"] == "Looks good"
    assert body["task_id"] == task.id


async def test_create_rejects_a_blank_body(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.post(
        f"/api/tasks/{task.id}/comments/",
        headers=auth_headers(user),
        json={"body": "   "},
    )

    assert response.status_code == 422


async def test_create_on_a_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, _workspace = await create_user_with_workspace(session)

    response = await client.post(
        "/api/tasks/999/comments/",
        headers=auth_headers(user),
        json={"body": "Ghost"},
    )

    assert response.status_code == 404


async def test_update_comment(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    comment = await create_comment(session, workspace, user, task, body="Old")

    response = await client.patch(
        f"/api/tasks/{task.id}/comments/{comment.id}/",
        headers=auth_headers(user),
        json={"body": "New"},
    )

    assert response.status_code == 200
    assert response.json()["body"] == "New"


async def test_update_rejects_a_blank_body(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    comment = await create_comment(session, workspace, user, task)

    response = await client.patch(
        f"/api/tasks/{task.id}/comments/{comment.id}/",
        headers=auth_headers(user),
        json={"body": ""},
    )

    assert response.status_code == 422


async def test_update_a_missing_comment_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.patch(
        f"/api/tasks/{task.id}/comments/999/",
        headers=auth_headers(user),
        json={"body": "X"},
    )

    assert response.status_code == 404


async def test_update_a_comment_under_the_wrong_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    other_task = await create_task(session, workspace)
    comment = await create_comment(session, workspace, user, task)

    # Right comment id, wrong task in the path: the pair does not match.
    response = await client.patch(
        f"/api/tasks/{other_task.id}/comments/{comment.id}/",
        headers=auth_headers(user),
        json={"body": "Sneaky"},
    )

    assert response.status_code == 404


async def test_delete_comment(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    comment = await create_comment(session, workspace, user, task)
    headers = auth_headers(user)

    response = await client.delete(
        f"/api/tasks/{task.id}/comments/{comment.id}/",
        headers=headers,
    )

    assert response.status_code == 204
    listed = await client.get(f"/api/tasks/{task.id}/comments/", headers=headers)
    assert listed.json() == []


async def test_delete_a_missing_comment_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.delete(
        f"/api/tasks/{task.id}/comments/999/",
        headers=auth_headers(user),
    )

    assert response.status_code == 404


async def test_deleting_a_task_removes_its_comments(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    await create_comment(session, workspace, user, task)
    headers = auth_headers(user)

    deleted = await client.delete(f"/api/tasks/{task.id}/", headers=headers)
    assert deleted.status_code == 204

    # The task is gone, so listing its comments 404s (cascade left nothing).
    orphaned = await client.get(f"/api/tasks/{task.id}/comments/", headers=headers)
    assert orphaned.status_code == 404


async def test_non_member_cannot_list_a_tasks_comments(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    await create_comment(session, workspace, owner, task)
    intruder = await create_user(session)

    response = await client.get(
        f"/api/tasks/{task.id}/comments/",
        headers=auth_headers(intruder, workspace),
    )

    assert response.status_code == 404


async def test_non_member_cannot_update_a_comment(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    comment = await create_comment(session, workspace, owner, task, body="Private")
    intruder = await create_user(session)

    response = await client.patch(
        f"/api/tasks/{task.id}/comments/{comment.id}/",
        headers=auth_headers(intruder, workspace),
        json={"body": "Hijacked"},
    )

    assert response.status_code == 404
