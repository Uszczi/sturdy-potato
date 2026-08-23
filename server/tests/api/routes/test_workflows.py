"""The workflow endpoints: reading a board's columns and replacing them."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    auth_headers,
    create_project,
    create_task,
    create_user,
    create_user_with_workspace,
)
from use_cases.workflow import Status, Workflow

# The three-column board most of these tests replace the default with.
THREE_COLUMN = [
    {"key": "todo", "label": "Todo", "is_initial": True, "is_terminal": False},
    {"key": "doing", "label": "Doing", "is_initial": False, "is_terminal": False},
    {"key": "shipped", "label": "Shipped", "is_initial": False, "is_terminal": True},
]
FROM_DEFAULT = {"open": "todo", "done": "shipped"}


def _workflow(*statuses: dict[str, object]) -> Workflow:
    return Workflow(
        tuple(
            Status(
                key=str(s["key"]),
                label=str(s["label"]),
                is_initial=bool(s["is_initial"]),
                is_terminal=bool(s["is_terminal"]),
            )
            for s in statuses
        )
    )


async def test_project_detail_carries_its_workflow(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/",
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    assert [s["key"] for s in response.json()["workflow"]] == ["open", "done"]


async def test_project_list_omits_the_workflow(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await create_project(session, workspace)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/projects/", headers=auth_headers(user)
    )

    # Only the board view needs the columns, so the sidebar's list stays lean.
    assert "workflow" not in response.json()[0]


async def test_workspace_detail_carries_the_inbox_workflow(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/", headers=auth_headers(user)
    )

    assert response.status_code == 200
    assert [s["label"] for s in response.json()["workflow"]] == ["Open", "Done"]


async def test_a_non_member_cannot_read_a_workspace(
    client: AsyncClient, session: AsyncSession
) -> None:
    _, workspace = await create_user_with_workspace(session)
    outsider = await create_user(session)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/", headers=auth_headers(outsider)
    )

    assert response.status_code == 404


async def test_replacing_a_project_workflow_changes_its_columns(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)

    response = await client.put(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": THREE_COLUMN, "reassign": FROM_DEFAULT},
    )

    assert response.status_code == 200
    assert [s["key"] for s in response.json()["workflow"]] == [
        "todo",
        "doing",
        "shipped",
    ]


async def test_replacing_a_workflow_moves_the_tasks_standing_on_it(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    open_task = await create_task(session, workspace, project=project, status="open")
    done_task = await create_task(session, workspace, project=project, status="done")

    await client.put(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": THREE_COLUMN, "reassign": FROM_DEFAULT},
    )

    tasks = {
        task["id"]: task
        for task in (
            await client.get(
                f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
            )
        ).json()
    }
    assert (tasks[open_task.id]["status"], tasks[open_task.id]["is_done"]) == (
        "todo",
        False,
    )
    assert (tasks[done_task.id]["status"], tasks[done_task.id]["is_done"]) == (
        "shipped",
        True,
    )


async def test_reordering_columns_leaves_the_tasks_where_they_are(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    task = await create_task(session, workspace, project=project, status="done")
    reversed_order = [
        {"key": "done", "label": "Done", "is_initial": False, "is_terminal": True},
        {"key": "open", "label": "Open", "is_initial": True, "is_terminal": False},
    ]

    response = await client.put(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": reversed_order},
    )

    assert [s["key"] for s in response.json()["workflow"]] == ["done", "open"]
    retrieved = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/", headers=auth_headers(user)
    )
    assert retrieved.json()["status"] == "done"


async def test_renaming_a_label_keeps_the_key(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    task = await create_task(session, workspace, project=project)
    renamed = [
        {
            "key": "open",
            "label": "  Backlog  ",
            "is_initial": True,
            "is_terminal": False,
        },
        {"key": "done", "label": "Done", "is_initial": False, "is_terminal": True},
    ]

    response = await client.put(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": renamed},
    )

    assert response.json()["workflow"][0]["label"] == "Backlog"
    retrieved = await client.get(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/", headers=auth_headers(user)
    )
    # No task row is rewritten by a rename: the key is what they store.
    assert retrieved.json()["status"] == "open"


async def test_dropping_a_status_without_a_target_is_rejected(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)

    response = await client.put(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": THREE_COLUMN},
    )

    assert response.status_code == 400
    assert "needs a status to move" in response.json()["detail"]


async def test_a_workflow_without_an_ending_is_rejected(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(session, workspace)
    no_ending = [
        {"key": "todo", "label": "Todo", "is_initial": True, "is_terminal": False},
        {"key": "doing", "label": "Doing", "is_initial": False, "is_terminal": False},
    ]

    response = await client.put(
        f"/api/workspaces/{workspace.id}/projects/{project.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": no_ending, "reassign": {"open": "todo", "done": "doing"}},
    )

    assert response.status_code == 400
    assert "at least one terminal" in response.json()["detail"]


async def test_setting_the_workflow_of_a_missing_project_is_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)

    response = await client.put(
        f"/api/workspaces/{workspace.id}/projects/999/statuses/",
        headers=auth_headers(user),
        json={"statuses": THREE_COLUMN, "reassign": FROM_DEFAULT},
    )

    assert response.status_code == 404


async def test_replacing_the_workspace_workflow_resettles_the_inbox(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    inbox_task = await create_task(session, workspace)
    project = await create_project(session, workspace)
    project_task = await create_task(session, workspace, project=project)

    response = await client.put(
        f"/api/workspaces/{workspace.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": THREE_COLUMN, "reassign": FROM_DEFAULT},
    )

    assert response.status_code == 200
    tasks = {
        task["id"]: task
        for task in (
            await client.get(
                f"/api/workspaces/{workspace.id}/tasks/", headers=auth_headers(user)
            )
        ).json()
    }
    assert tasks[inbox_task.id]["status"] == "todo"
    # The project holds its own snapshot, so the default's edit skips it.
    assert tasks[project_task.id]["status"] == "open"


async def test_a_new_project_copies_the_workspace_workflow(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    await client.put(
        f"/api/workspaces/{workspace.id}/statuses/",
        headers=auth_headers(user),
        json={"statuses": THREE_COLUMN, "reassign": FROM_DEFAULT},
    )

    created = await client.post(
        f"/api/workspaces/{workspace.id}/projects/",
        headers=auth_headers(user),
        json={"name": "Fresh"},
    )
    detail = await client.get(
        f"/api/workspaces/{workspace.id}/projects/{created.json()['id']}/",
        headers=auth_headers(user),
    )

    assert [s["key"] for s in detail.json()["workflow"]] == ["todo", "doing", "shipped"]


async def test_a_task_starts_in_its_boards_initial_status(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(
        session, workspace, workflow=_workflow(*THREE_COLUMN)
    )

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/",
        headers=auth_headers(user),
        json={"title": "Ship it", "project_id": project.id},
    )

    assert response.status_code == 201
    assert (response.json()["status"], response.json()["is_done"]) == ("todo", False)


async def test_a_task_cannot_be_created_in_another_boards_status(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(
        session, workspace, workflow=_workflow(*THREE_COLUMN)
    )

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/",
        headers=auth_headers(user),
        json={"title": "Ship it", "project_id": project.id, "status": "open"},
    )

    assert response.status_code == 400
    assert "not a status of this workflow" in response.json()["detail"]


async def test_a_card_cannot_be_dragged_to_a_column_the_board_lacks(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    project = await create_project(
        session, workspace, workflow=_workflow(*THREE_COLUMN)
    )
    task = await create_task(session, workspace, project=project, status="doing")

    response = await client.post(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/move/",
        headers=auth_headers(user),
        json={"status": "done", "position": 0},
    )

    assert response.status_code == 400


async def test_moving_a_task_to_a_board_without_its_status_maps_it(
    client: AsyncClient, session: AsyncSession
) -> None:
    user, workspace = await create_user_with_workspace(session)
    rich = await create_project(
        session, workspace, name="Rich", workflow=_workflow(*THREE_COLUMN)
    )
    simple = await create_project(session, workspace, name="Simple")
    task = await create_task(session, workspace, project=rich, status="shipped")

    response = await client.patch(
        f"/api/workspaces/{workspace.id}/tasks/{task.id}/",
        headers=auth_headers(user),
        json={"project_id": simple.id},
    )

    # Finished work stays finished: it lands in the destination's terminal.
    assert (response.json()["status"], response.json()["is_done"]) == ("done", True)
