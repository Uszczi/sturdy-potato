from datetime import UTC, date, datetime, timedelta

from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models import utcnow
from tests.factories import auth_headers, create_project, create_task, create_user


async def test_list_returns_only_the_authenticated_users_tasks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    await create_task(session, user, title="Mine")
    other = await create_user(session)
    await create_task(session, other, title="Theirs")

    response = await client.get("/api/tasks/", headers=auth_headers(user))

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Mine"]


async def test_list_orders_by_position_then_newest(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    with freeze_time("2024-01-01T12:00:00Z", auto_tick_seconds=1):
        await create_task(session, user, title="Older", position=0)
        await create_task(session, user, title="Newer", position=0)

    response = await client.get("/api/tasks/", headers=auth_headers(user))

    # Same position falls back to newest-created first.
    assert [task["title"] for task in response.json()] == ["Newer", "Older"]


async def test_list_sinks_completed_below_open_ignoring_position(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    # The completed task has the lower position, yet must still sort last.
    await create_task(session, user, title="Done", completed=True, position=0)
    await create_task(session, user, title="Open", position=1)

    response = await client.get("/api/tasks/", headers=auth_headers(user))

    assert [task["title"] for task in response.json()] == ["Open", "Done"]


async def test_completed_tasks_sort_most_recently_completed_first(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    earlier = await create_task(
        session, user, title="Earlier", completed=True, position=0
    )
    later = await create_task(session, user, title="Later", completed=True, position=1)
    # `later` was created last, but `earlier` was ticked most recently, so its
    # newer updated_at should lead the completed group (top of closed).
    earlier.updated_at = datetime(2024, 2, 1, tzinfo=UTC)
    later.updated_at = datetime(2024, 1, 1, tzinfo=UTC)
    session.add_all([earlier, later])
    await session.commit()

    response = await client.get("/api/tasks/", headers=auth_headers(user))
    assert [task["title"] for task in response.json()] == ["Earlier", "Later"]


async def test_reopening_a_task_returns_it_to_the_open_group(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    await create_task(session, user, title="Open", position=0)
    done = await create_task(
        session, user, title="Reopened", completed=True, position=1
    )
    headers = auth_headers(user)

    await client.patch(
        f"/api/tasks/{done.id}/", headers=headers, json={"completed": False}
    )

    response = await client.get("/api/tasks/", headers=headers)
    # Back among the open tasks, ordered by its position.
    assert [task["title"] for task in response.json()] == ["Open", "Reopened"]


async def test_create_task(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)

    response = await client.post(
        "/api/tasks/", headers=auth_headers(user), json={"title": "Write docs"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write docs"
    assert body["project_id"] is None


async def test_create_task_rejects_a_blank_title(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.post(
        "/api/tasks/", headers=auth_headers(user), json={"title": "   "}
    )

    assert response.status_code == 422


async def test_create_task_assigned_to_a_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user)

    response = await client.post(
        "/api/tasks/",
        headers=auth_headers(user),
        json={"title": "Scoped", "project_id": project.id},
    )

    assert response.status_code == 201
    assert response.json()["project_id"] == project.id


async def test_create_task_rejects_another_users_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    other = await create_user(session)
    project = await create_project(session, other)

    response = await client.post(
        "/api/tasks/",
        headers=auth_headers(user),
        json={"title": "Sneaky", "project_id": project.id},
    )

    assert response.status_code == 404


async def test_retrieve_task(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    task = await create_task(session, user, title="Find me")

    response = await client.get(f"/api/tasks/{task.id}/", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


async def test_retrieve_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.get("/api/tasks/999/", headers=auth_headers(user))

    assert response.status_code == 404


async def test_update_task_fields(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    task = await create_task(session, user, title="Old", completed=False)

    response = await client.patch(
        f"/api/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"title": "New", "completed": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New"
    assert body["completed"] is True


async def test_update_task_rejects_null_title(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    task = await create_task(session, user)

    response = await client.patch(
        f"/api/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"title": None},
    )

    assert response.status_code == 422


async def test_update_task_can_clear_the_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user)
    task = await create_task(session, user, project=project)

    response = await client.patch(
        f"/api/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"project_id": None},
    )

    assert response.status_code == 200
    assert response.json()["project_id"] is None


async def test_update_task_rejects_another_users_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    task = await create_task(session, user)
    other = await create_user(session)
    project = await create_project(session, other)

    response = await client.patch(
        f"/api/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"project_id": project.id},
    )

    assert response.status_code == 404


async def test_update_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.patch(
        "/api/tasks/999/", headers=auth_headers(user), json={"title": "X"}
    )

    assert response.status_code == 404


async def test_delete_task(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    task = await create_task(session, user)

    response = await client.delete(f"/api/tasks/{task.id}/", headers=auth_headers(user))

    assert response.status_code == 204
    follow_up = await client.get(f"/api/tasks/{task.id}/", headers=auth_headers(user))
    assert follow_up.status_code == 404


async def test_delete_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.delete("/api/tasks/999/", headers=auth_headers(user))

    assert response.status_code == 404


async def test_reorder_tasks(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    first = await create_task(session, user, title="First", position=0)
    second = await create_task(session, user, title="Second", position=1)

    response = await client.post(
        "/api/tasks/reorder/",
        headers=auth_headers(user),
        json={"order": [second.id, first.id]},
    )

    assert response.status_code == 204
    listed = await client.get("/api/tasks/", headers=auth_headers(user))
    assert [task["id"] for task in listed.json()] == [second.id, first.id]


async def test_reorder_rejects_another_users_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    task = await create_task(session, user)
    other = await create_user(session)
    foreign = await create_task(session, other)

    response = await client.post(
        "/api/tasks/reorder/",
        headers=auth_headers(user),
        json={"order": [task.id, foreign.id]},
    )

    assert response.status_code == 400


async def test_reorder_with_an_empty_order_is_a_noop(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.post(
        "/api/tasks/reorder/", headers=auth_headers(user), json={"order": []}
    )

    assert response.status_code == 204


async def test_reorder_rejects_duplicate_ids(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    task = await create_task(session, user)

    response = await client.post(
        "/api/tasks/reorder/",
        headers=auth_headers(user),
        json={"order": [task.id, task.id]},
    )

    assert response.status_code == 422


async def test_view_inbox_returns_unassigned_tasks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user)
    await create_task(session, user, title="Loose")
    await create_task(session, user, title="Scoped", project=project)

    response = await client.get(
        "/api/tasks/view/", headers=auth_headers(user), params={"view": "inbox"}
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Loose"]


async def test_view_by_project(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    project = await create_project(session, user)
    await create_task(session, user, title="Scoped", project=project)
    await create_task(session, user, title="Loose")

    response = await client.get(
        "/api/tasks/view/",
        headers=auth_headers(user),
        params={"project": project.id},
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Scoped"]


async def test_view_rejects_another_users_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    other = await create_user(session)
    project = await create_project(session, other)

    response = await client.get(
        "/api/tasks/view/",
        headers=auth_headers(user),
        params={"project": project.id},
    )

    assert response.status_code == 404


async def test_view_today_and_upcoming(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    today = utcnow().date()
    await create_task(session, user, title="Due today", due_date=today)
    await create_task(
        session, user, title="Due later", due_date=today + timedelta(days=3)
    )

    today_response = await client.get(
        "/api/tasks/view/", headers=auth_headers(user), params={"view": "today"}
    )
    upcoming_response = await client.get(
        "/api/tasks/view/", headers=auth_headers(user), params={"view": "upcoming"}
    )

    assert [t["title"] for t in today_response.json()] == ["Due today"]
    assert [t["title"] for t in upcoming_response.json()] == ["Due later"]


@freeze_time("2026-08-19 23:30:00")
async def test_view_today_respects_client_timezone(
    client: AsyncClient, session: AsyncSession
) -> None:
    # At this instant it is still Aug 19 in UTC but already Aug 20 in UTC+14.
    user = await create_user(session)
    await create_task(session, user, title="Local tomorrow", due_date=date(2026, 8, 20))

    default_view = await client.get(
        "/api/tasks/view/", headers=auth_headers(user), params={"view": "today"}
    )
    ahead_view = await client.get(
        "/api/tasks/view/",
        headers=auth_headers(user),
        params={"view": "today", "tz": "Pacific/Kiritimati"},
    )

    assert [t["title"] for t in default_view.json()] == []
    assert [t["title"] for t in ahead_view.json()] == ["Local tomorrow"]


async def test_view_rejects_an_unknown_timezone(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)

    response = await client.get(
        "/api/tasks/view/",
        headers=auth_headers(user),
        params={"view": "today", "tz": "Mars/Phobos"},
    )

    assert response.status_code == 400


async def test_view_all_returns_everything(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    project = await create_project(session, user)
    await create_task(session, user, title="Loose")
    await create_task(session, user, title="Scoped", project=project)

    response = await client.get(
        "/api/tasks/view/", headers=auth_headers(user), params={"view": "all"}
    )

    assert {task["title"] for task in response.json()} == {"Loose", "Scoped"}


async def test_open_tasks_with_limit(
    client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(session)
    await create_task(session, user, title="Open 1", position=0)
    await create_task(session, user, title="Open 2", position=1)
    await create_task(session, user, title="Done", completed=True, position=2)

    unlimited = await client.get("/api/tasks/open/", headers=auth_headers(user))
    limited = await client.get(
        "/api/tasks/open/", headers=auth_headers(user), params={"limit": 1}
    )

    assert [t["title"] for t in unlimited.json()] == ["Open 1", "Open 2"]
    assert [t["title"] for t in limited.json()] == ["Open 1"]


async def test_count_tasks(client: AsyncClient, session: AsyncSession) -> None:
    user = await create_user(session)
    await create_task(session, user, completed=False)
    await create_task(session, user, completed=True)

    total = await client.get("/api/tasks/count/", headers=auth_headers(user))
    open_only = await client.get(
        "/api/tasks/count/", headers=auth_headers(user), params={"completed": "false"}
    )

    assert total.json() == {"count": 2}
    assert open_only.json() == {"count": 1}


async def test_cannot_retrieve_another_users_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner = await create_user(session)
    task = await create_task(session, owner, title="Private")
    intruder = await create_user(session)

    response = await client.get(
        f"/api/tasks/{task.id}/", headers=auth_headers(intruder)
    )

    assert response.status_code == 404


async def test_cannot_update_another_users_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner = await create_user(session)
    task = await create_task(session, owner, title="Private")
    intruder = await create_user(session)

    response = await client.patch(
        f"/api/tasks/{task.id}/",
        headers=auth_headers(intruder),
        json={"title": "Hijacked"},
    )

    assert response.status_code == 404


async def test_cannot_delete_another_users_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner = await create_user(session)
    task = await create_task(session, owner, title="Private")
    intruder = await create_user(session)

    response = await client.delete(
        f"/api/tasks/{task.id}/", headers=auth_headers(intruder)
    )

    assert response.status_code == 404
    # The owner can still see it: the delete never touched their row.
    still_there = await client.get(
        f"/api/tasks/{task.id}/", headers=auth_headers(owner)
    )
    assert still_there.status_code == 200
