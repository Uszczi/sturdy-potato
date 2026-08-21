from datetime import UTC, date, datetime, timedelta

from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models import utcnow
from tests.factories import (
    auth_headers,
    create_project,
    create_task,
    create_user,
    create_user_with_workspace,
)
from use_cases.task_status import TaskStatus


async def test_list_returns_only_the_workspaces_tasks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_task(session, workspace, title="Mine")
    _other, other_workspace = await create_user_with_workspace(session)
    await create_task(session, other_workspace, title="Theirs")

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
    )

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Mine"]


async def test_list_orders_by_position_then_newest(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    with freeze_time("2024-01-01T12:00:00Z", auto_tick_seconds=1):
        await create_task(session, workspace, title="Older", position=0)
        await create_task(session, workspace, title="Newer", position=0)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
    )

    # Same position falls back to newest-created first.
    assert [task["title"] for task in response.json()] == ["Newer", "Older"]


async def test_list_sinks_completed_below_open_ignoring_position(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    # The done task has the lower position, yet must still sort last.
    await create_task(
        session, workspace, title="Done", status=TaskStatus.DONE, position=0
    )
    await create_task(session, workspace, title="Open", position=1)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
    )

    assert [task["title"] for task in response.json()] == ["Open", "Done"]


async def test_completed_tasks_sort_by_manual_position(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    # `first` has the lower position but the older updated_at: the done column is
    # manually sortable, so position wins over completion recency.
    first = await create_task(
        session, workspace, title="First", status=TaskStatus.DONE, position=0
    )
    second = await create_task(
        session, workspace, title="Second", status=TaskStatus.DONE, position=1
    )
    first.updated_at = datetime(2024, 1, 1, tzinfo=UTC)
    second.updated_at = datetime(2024, 2, 1, tzinfo=UTC)
    session.add_all([first, second])
    await session.commit()

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
    )
    assert [task["title"] for task in response.json()] == ["First", "Second"]


async def test_reopening_a_task_returns_it_to_the_open_group(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_task(session, workspace, title="Open", position=0)
    done = await create_task(
        session, workspace, title="Reopened", status=TaskStatus.DONE, position=1
    )
    headers = auth_headers(user)

    await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{done.id}/",
        headers=headers,
        json={"status": "open"},
    )

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/", headers=headers
    )
    # Back among the open tasks, ordered by its position.
    assert [task["title"] for task in response.json()] == ["Open", "Reopened"]


async def test_create_task(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/",
        headers=auth_headers(user),
        json={"title": "Write docs"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write docs"
    assert body["project_id"] is None


async def test_create_task_rejects_a_blank_title(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/",
        headers=auth_headers(user),
        json={"title": "   "},
    )

    assert response.status_code == 422


async def test_create_task_assigned_to_a_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/",
        headers=auth_headers(user),
        json={"title": "Scoped", "project_id": project.id},
    )

    assert response.status_code == 201
    assert response.json()["project_id"] == project.id


async def test_create_task_rejects_a_project_from_another_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    _other, other_workspace = await create_user_with_workspace(session)
    project = await create_project(session, other_workspace)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/",
        headers=auth_headers(user),
        json={"title": "Sneaky", "project_id": project.id},
    )

    assert response.status_code == 404


async def test_retrieve_task(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace, title="Find me")

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/", headers=auth_headers(user)
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


async def test_retrieve_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/999/", headers=auth_headers(user)
    )

    assert response.status_code == 404


async def test_update_task_fields(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace, title="Old", status=TaskStatus.OPEN)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"title": "New", "status": "done"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New"
    assert body["status"] == "done"


async def test_update_task_rejects_null_title(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"title": None},
    )

    assert response.status_code == 422


async def test_update_task_can_clear_the_project(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    task = await create_task(session, workspace, project=project)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"project_id": None},
    )

    assert response.status_code == 200
    assert response.json()["project_id"] is None


async def test_reassigning_to_a_project_appends_to_its_column(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    # The project already has one open task at slot 0.
    await create_task(session, workspace, title="Resident", project=project)
    loose = await create_task(session, workspace, title="Loose")
    headers = auth_headers(user)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{loose.id}/",
        headers=headers,
        json={"project_id": project.id},
    )

    assert response.status_code == 200
    # It joins the project's open column at the end (slot 1), after the resident.
    assert response.json()["position"] == 1
    board = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=headers,
        params={"project": project.id},
    )
    assert [task["title"] for task in board.json()] == ["Resident", "Loose"]


async def test_update_task_rejects_a_project_from_another_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)
    _other, other_workspace = await create_user_with_workspace(session)
    project = await create_project(session, other_workspace)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"project_id": project.id},
    )

    assert response.status_code == 404


async def test_update_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/999/",
        headers=auth_headers(user),
        json={"title": "X"},
    )

    assert response.status_code == 404


async def test_delete_task(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.delete(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/", headers=auth_headers(user)
    )

    assert response.status_code == 204
    follow_up = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/", headers=auth_headers(user)
    )
    assert follow_up.status_code == 404


async def test_delete_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.delete(
        f"/api/workspaces/{workspace.id}/tasks/999/", headers=auth_headers(user)
    )

    assert response.status_code == 404


async def test_move_task_across_columns_and_persists(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    first = await create_task(session, workspace, title="First", position=0)
    second = await create_task(session, workspace, title="Second", position=1)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/{second.id}/move/",
        headers=auth_headers(user),
        json={"status": TaskStatus.DONE.value, "position": 0},
    )

    assert response.status_code == 204
    listed = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
    )
    tasks_by_id = {task["id"]: task for task in listed.json()}
    assert tasks_by_id[second.id]["status"] == TaskStatus.DONE.value
    # Open column keeps First; Second now leads the done column.
    assert [t["id"] for t in listed.json()] == [first.id, second.id]


async def test_move_missing_task_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/999/move/",
        headers=auth_headers(user),
        json={"status": TaskStatus.OPEN.value, "position": 0},
    )

    assert response.status_code == 404


async def test_move_rejects_negative_position(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/move/",
        headers=auth_headers(user),
        json={"status": TaskStatus.OPEN.value, "position": -1},
    )

    assert response.status_code == 422


async def test_view_inbox_returns_unassigned_tasks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    await create_task(session, workspace, title="Loose")
    await create_task(session, workspace, title="Scoped", project=project)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "inbox"},
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Loose"]


async def test_view_by_project(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    await create_task(session, workspace, title="Scoped", project=project)
    await create_task(session, workspace, title="Loose")

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"project": project.id},
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Scoped"]


async def test_view_rejects_a_project_from_another_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    _other, other_workspace = await create_user_with_workspace(session)
    project = await create_project(session, other_workspace)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"project": project.id},
    )

    assert response.status_code == 404


async def test_view_today_and_upcoming(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    today = utcnow().date()
    await create_task(session, workspace, title="Due today", due_date=today)
    await create_task(
        session, workspace, title="Due later", due_date=today + timedelta(days=3)
    )

    today_response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "today"},
    )
    upcoming_response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "upcoming"},
    )

    assert [t["title"] for t in today_response.json()] == ["Due today"]
    assert [t["title"] for t in upcoming_response.json()] == ["Due later"]


@freeze_time("2026-08-19 23:30:00")
async def test_view_today_respects_client_timezone(
    client: AsyncClient, session: AsyncSession
) -> None:
    # At this instant it is still Aug 19 in UTC but already Aug 20 in UTC+14.
    user, workspace = await create_user_with_workspace(session)
    await create_task(
        session, workspace, title="Local tomorrow", due_date=date(2026, 8, 20)
    )

    default_view = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "today"},
    )
    ahead_view = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "today", "tz": "Pacific/Kiritimati"},
    )

    assert [t["title"] for t in default_view.json()] == []
    assert [t["title"] for t in ahead_view.json()] == ["Local tomorrow"]


async def test_view_rejects_an_unknown_timezone(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "today", "tz": "Mars/Phobos"},
    )

    assert response.status_code == 400


async def test_view_all_returns_everything(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    await create_task(session, workspace, title="Loose")
    await create_task(session, workspace, title="Scoped", project=project)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/view/",
        headers=auth_headers(user),
        params={"view": "all"},
    )

    assert {task["title"] for task in response.json()} == {"Loose", "Scoped"}


async def test_open_tasks_with_limit(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_task(session, workspace, title="Open 1", position=0)
    await create_task(session, workspace, title="Open 2", position=1)
    await create_task(
        session, workspace, title="Done", status=TaskStatus.DONE, position=2
    )

    unlimited = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/open/", headers=auth_headers(user)
    )
    limited = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/open/",
        headers=auth_headers(user),
        params={"limit": 1},
    )

    assert [t["title"] for t in unlimited.json()] == ["Open 1", "Open 2"]
    assert [t["title"] for t in limited.json()] == ["Open 1"]


async def test_count_tasks(client: AsyncClient, session: AsyncSession) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_task(session, workspace, status=TaskStatus.OPEN)
    await create_task(session, workspace, status=TaskStatus.DONE)

    total = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/count/", headers=auth_headers(user)
    )
    open_only = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/count/",
        headers=auth_headers(user),
        params={"status": "open"},
    )

    assert total.json() == {"count": 2}
    assert open_only.json() == {"count": 1}


async def test_non_member_cannot_retrieve_a_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    _owner, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace, title="Private")
    intruder = await create_user(session)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(intruder),
    )

    assert response.status_code == 404


async def test_non_member_cannot_update_a_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    _owner, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace, title="Private")
    intruder = await create_user(session)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(intruder),
        json={"title": "Hijacked"},
    )

    assert response.status_code == 404


async def test_non_member_cannot_delete_a_task(
    client: AsyncClient, session: AsyncSession
) -> None:
    owner, workspace = await create_user_with_workspace(session)
    task = await create_task(session, workspace, title="Private")
    intruder = await create_user(session)

    response = await client.delete(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(intruder),
    )

    assert response.status_code == 404
    # The owner can still see it: the delete never touched their row.
    still_there = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/", headers=auth_headers(owner)
    )
    assert still_there.status_code == 200
