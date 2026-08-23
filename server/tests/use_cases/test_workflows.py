"""Editing a board's workflow, and what that does to the tasks standing on it."""

from datetime import UTC, datetime

import pytest

from tests.fakes import (
    FakeProjectRepository,
    FakeTaskRepository,
    FakeWorkspaceRepository,
)
from use_cases.dtos import (
    ProjectCreateData,
    TaskCreateData,
    TaskUpdateData,
    WorkflowUpdateData,
)
from use_cases.entities import Project, Task, Workspace
from use_cases.exceptions import (
    InvalidWorkflow,
    ProjectNotFound,
    UnknownStatus,
    WorkspaceNotFound,
)
from use_cases.projects.create_project import CreateProject
from use_cases.tasks.create_task import CreateTask
from use_cases.tasks.move_task import MoveTask
from use_cases.tasks.update_task import UpdateTask
from use_cases.workflow import DEFAULT_WORKFLOW, Status, Workflow
from use_cases.workflows.set_project_workflow import SetProjectWorkflow
from use_cases.workflows.set_workspace_workflow import SetWorkspaceWorkflow
from use_cases.workspaces.get_workspace import GetWorkspace

WORKSPACE = 1
NOW = datetime(2024, 1, 1, tzinfo=UTC)

# A three-column board: work moves Todo -> Doing -> Shipped.
TODO = Status(key="todo", label="Todo", is_initial=True)
DOING = Status(key="doing", label="Doing")
SHIPPED = Status(key="shipped", label="Shipped", is_terminal=True)
CANCELLED = Status(key="cancelled", label="Cancelled", is_terminal=True)
THREE_COLUMN = Workflow((TODO, DOING, SHIPPED))


def _workspace(workflow: Workflow = DEFAULT_WORKFLOW) -> Workspace:
    return Workspace(
        id=WORKSPACE,
        name="Personal",
        workflow=workflow,
        is_personal=True,
        created_at=NOW,
        updated_at=NOW,
    )


def _project(
    project_id: int, *, workflow: Workflow = DEFAULT_WORKFLOW, name: str = "Work"
) -> Project:
    return Project(
        id=project_id,
        workspace_id=WORKSPACE,
        name=name,
        color=None,
        workflow=workflow,
        position=0,
        task_count=0,
        created_at=NOW,
        updated_at=NOW,
    )


def _task(
    task_id: int,
    *,
    status: str,
    is_done: bool = False,
    position: int = 0,
    project_id: int | None = None,
) -> Task:
    return Task(
        id=task_id,
        workspace_id=WORKSPACE,
        project_id=project_id,
        title=f"Task {task_id}",
        description="",
        status=status,
        is_done=is_done,
        position=position,
        due_date=None,
        created_at=NOW,
        updated_at=NOW,
    )


def _update(statuses: Workflow, **reassign: str) -> WorkflowUpdateData:
    return WorkflowUpdateData(statuses=statuses.statuses, reassign=reassign)


# --- setting a project's workflow -------------------------------------------


async def test_replacing_a_workflow_stores_the_new_order() -> None:
    projects = FakeProjectRepository([_project(1)])
    tasks = FakeTaskRepository()

    updated = await SetProjectWorkflow(projects, tasks).execute(
        WORKSPACE, 1, _update(THREE_COLUMN, open="todo", done="shipped")
    )

    assert updated.workflow.keys == ("todo", "doing", "shipped")


async def test_a_missing_project_is_not_found() -> None:
    with pytest.raises(ProjectNotFound):
        await SetProjectWorkflow(FakeProjectRepository(), FakeTaskRepository()).execute(
            WORKSPACE, 999, _update(THREE_COLUMN)
        )


async def test_an_invalid_workflow_is_rejected() -> None:
    projects = FakeProjectRepository([_project(1)])
    # No terminal status, so nothing on this board would ever count as finished.
    no_ending = WorkflowUpdateData(statuses=(TODO, DOING), reassign={})

    with pytest.raises(InvalidWorkflow, match="at least one terminal"):
        await SetProjectWorkflow(projects, FakeTaskRepository()).execute(
            WORKSPACE, 1, no_ending
        )


async def test_dropping_a_status_without_a_target_is_rejected() -> None:
    projects = FakeProjectRepository([_project(1)])

    # "open" and "done" both vanish, and neither names where its tasks go.
    with pytest.raises(InvalidWorkflow, match="needs a status to move"):
        await SetProjectWorkflow(projects, FakeTaskRepository()).execute(
            WORKSPACE, 1, _update(THREE_COLUMN)
        )


async def test_reassigning_a_status_that_survives_is_rejected() -> None:
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    kept = Workflow((TODO, DOING, SHIPPED, CANCELLED))

    with pytest.raises(InvalidWorkflow, match="not being removed"):
        await SetProjectWorkflow(projects, FakeTaskRepository()).execute(
            WORKSPACE, 1, _update(kept, doing="shipped")
        )


async def test_reassigning_to_a_status_that_does_not_exist_is_rejected() -> None:
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    without_doing = Workflow((TODO, SHIPPED))

    with pytest.raises(InvalidWorkflow, match="no such status"):
        await SetProjectWorkflow(projects, FakeTaskRepository()).execute(
            WORKSPACE, 1, _update(without_doing, doing="nowhere")
        )


async def test_removing_a_status_moves_its_tasks_to_the_named_target() -> None:
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    tasks = FakeTaskRepository(
        [
            _task(1, status="doing", project_id=1),
            _task(2, status="todo", project_id=1),
        ]
    )
    without_doing = Workflow((TODO, SHIPPED))

    await SetProjectWorkflow(projects, tasks).execute(
        WORKSPACE, 1, _update(without_doing, doing="todo")
    )

    moved = await tasks.get(WORKSPACE, 1)
    assert moved is not None
    assert (moved.status, moved.is_done) == ("todo", False)


async def test_a_merged_column_is_renumbered_from_zero() -> None:
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    tasks = FakeTaskRepository(
        [
            _task(1, status="todo", position=0, project_id=1),
            _task(2, status="todo", position=1, project_id=1),
            _task(3, status="doing", position=0, project_id=1),
        ]
    )
    without_doing = Workflow((TODO, SHIPPED))

    await SetProjectWorkflow(projects, tasks).execute(
        WORKSPACE, 1, _update(without_doing, doing="todo")
    )

    # Todo's own tasks keep their order and the collapsed column stacks below,
    # rather than the two interleaving by their old positions.
    slots = {t.id: t.position for t in await tasks.list_all(WORKSPACE)}
    assert (slots[1], slots[2], slots[3]) == (0, 1, 2)


async def test_making_a_status_terminal_marks_its_tasks_done() -> None:
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    tasks = FakeTaskRepository([_task(1, status="doing", project_id=1)])
    doing_is_terminal = Workflow(
        (TODO, Status(key="doing", label="Doing", is_terminal=True), SHIPPED)
    )

    await SetProjectWorkflow(projects, tasks).execute(
        WORKSPACE, 1, _update(doing_is_terminal)
    )

    settled = await tasks.get(WORKSPACE, 1)
    assert settled is not None and settled.is_done is True


async def test_renaming_a_label_leaves_the_tasks_alone() -> None:
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    tasks = FakeTaskRepository([_task(1, status="doing", position=3, project_id=1)])
    renamed = Workflow((TODO, Status(key="doing", label="In Progress"), SHIPPED))

    await SetProjectWorkflow(projects, tasks).execute(WORKSPACE, 1, _update(renamed))

    # The key is what a task stores, so a label change is a one-row edit.
    kept = await tasks.get(WORKSPACE, 1)
    assert kept is not None and kept.status == "doing"


async def test_another_projects_tasks_are_untouched() -> None:
    projects = FakeProjectRepository(
        [
            _project(1, workflow=THREE_COLUMN),
            _project(2, workflow=THREE_COLUMN, name="Other"),
        ]
    )
    tasks = FakeTaskRepository([_task(9, status="doing", project_id=2)])

    await SetProjectWorkflow(projects, tasks).execute(
        WORKSPACE, 1, _update(Workflow((TODO, SHIPPED)), doing="todo")
    )

    untouched = await tasks.get(WORKSPACE, 9)
    assert untouched is not None and untouched.status == "doing"


# --- setting the workspace's workflow ----------------------------------------


async def test_the_workspace_workflow_resettles_inbox_tasks_only() -> None:
    workspaces = FakeWorkspaceRepository([_workspace()])
    tasks = FakeTaskRepository(
        [_task(1, status="open"), _task(2, status="open", project_id=7)]
    )

    await SetWorkspaceWorkflow(workspaces, tasks).execute(
        WORKSPACE, _update(THREE_COLUMN, open="todo", done="shipped")
    )

    inbox = await tasks.get(WORKSPACE, 1)
    in_project = await tasks.get(WORKSPACE, 2)
    assert inbox is not None and inbox.status == "todo"
    # A project holds its own snapshot, so editing the default skips it.
    assert in_project is not None and in_project.status == "open"


async def test_a_missing_workspace_is_not_found() -> None:
    with pytest.raises(WorkspaceNotFound):
        await SetWorkspaceWorkflow(
            FakeWorkspaceRepository(), FakeTaskRepository()
        ).execute(WORKSPACE, _update(THREE_COLUMN))


async def test_reading_a_missing_workspace_is_not_found() -> None:
    with pytest.raises(WorkspaceNotFound):
        await GetWorkspace(FakeWorkspaceRepository()).execute(WORKSPACE)


async def test_an_inbox_task_needs_its_workspace_to_exist() -> None:
    # Membership guards this over HTTP, so it is only reachable if a workspace
    # disappears mid-transaction; the board still refuses to resolve without it.
    with pytest.raises(WorkspaceNotFound):
        await CreateTask(
            FakeTaskRepository(), FakeProjectRepository(), FakeWorkspaceRepository()
        ).execute(WORKSPACE, _create_data(project_id=None))


async def test_creating_a_project_needs_its_workspace_to_exist() -> None:
    with pytest.raises(WorkspaceNotFound):
        await CreateProject(FakeProjectRepository(), FakeWorkspaceRepository()).execute(
            WORKSPACE, _project_data()
        )


# --- how tasks meet a workflow -----------------------------------------------


async def test_a_new_project_copies_the_workspace_workflow() -> None:
    workspaces = FakeWorkspaceRepository([_workspace(THREE_COLUMN)])
    projects = FakeProjectRepository()

    created = await CreateProject(projects, workspaces).execute(
        WORKSPACE, _project_data()
    )

    assert created.workflow.keys == ("todo", "doing", "shipped")


async def test_the_copy_does_not_follow_later_workspace_edits() -> None:
    workspaces = FakeWorkspaceRepository([_workspace(THREE_COLUMN)])
    projects = FakeProjectRepository()
    created = await CreateProject(projects, workspaces).execute(
        WORKSPACE, _project_data()
    )

    await SetWorkspaceWorkflow(workspaces, FakeTaskRepository()).execute(
        WORKSPACE, _update(DEFAULT_WORKFLOW, todo="open", doing="open", shipped="done")
    )

    unchanged = await projects.get(WORKSPACE, created.id)
    assert unchanged is not None
    assert unchanged.workflow.keys == ("todo", "doing", "shipped")


async def test_a_new_task_starts_in_its_boards_initial_status() -> None:
    workspaces = FakeWorkspaceRepository([_workspace()])
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    tasks = FakeTaskRepository()

    created = await CreateTask(tasks, projects, workspaces).execute(
        WORKSPACE, _create_data(project_id=1)
    )

    assert (created.status, created.is_done) == ("todo", False)


async def test_a_task_cannot_be_created_in_another_boards_status() -> None:
    workspaces = FakeWorkspaceRepository([_workspace()])
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])

    with pytest.raises(UnknownStatus):
        await CreateTask(FakeTaskRepository(), projects, workspaces).execute(
            WORKSPACE, _create_data(project_id=1, status="open")
        )


async def test_a_card_cannot_be_dragged_to_a_column_the_board_lacks() -> None:
    workspaces = FakeWorkspaceRepository([_workspace()])
    projects = FakeProjectRepository([_project(1, workflow=THREE_COLUMN)])
    tasks = FakeTaskRepository([_task(1, status="todo", project_id=1)])

    with pytest.raises(UnknownStatus):
        await MoveTask(tasks, projects, workspaces).execute(WORKSPACE, 1, "done", 0)


async def test_moving_to_a_project_without_the_status_lands_on_its_initial() -> None:
    workspaces = FakeWorkspaceRepository([_workspace()])
    projects = FakeProjectRepository(
        [_project(1, workflow=THREE_COLUMN), _project(2, name="Simple")]
    )
    tasks = FakeTaskRepository([_task(1, status="doing", project_id=1)])

    await UpdateTask(tasks, projects, workspaces).execute(
        WORKSPACE, 1, TaskUpdateData(project_id=2)
    )

    landed = await tasks.get(WORKSPACE, 1)
    assert landed is not None
    assert (landed.status, landed.is_done) == ("open", False)


async def test_moving_finished_work_keeps_it_finished() -> None:
    workspaces = FakeWorkspaceRepository([_workspace()])
    projects = FakeProjectRepository(
        [_project(1, workflow=THREE_COLUMN), _project(2, name="Simple")]
    )
    tasks = FakeTaskRepository([_task(1, status="shipped", is_done=True, project_id=1)])

    await UpdateTask(tasks, projects, workspaces).execute(
        WORKSPACE, 1, TaskUpdateData(project_id=2)
    )

    landed = await tasks.get(WORKSPACE, 1)
    assert landed is not None
    # "shipped" doesn't exist on the simple board, so it lands in its terminal.
    assert (landed.status, landed.is_done) == ("done", True)


async def test_a_shared_status_key_survives_the_move() -> None:
    shared = Workflow((TODO, DOING, CANCELLED))
    workspaces = FakeWorkspaceRepository([_workspace()])
    projects = FakeProjectRepository(
        [_project(1, workflow=THREE_COLUMN), _project(2, workflow=shared, name="Other")]
    )
    tasks = FakeTaskRepository([_task(1, status="doing", project_id=1)])

    await UpdateTask(tasks, projects, workspaces).execute(
        WORKSPACE, 1, TaskUpdateData(project_id=2)
    )

    landed = await tasks.get(WORKSPACE, 1)
    assert landed is not None and landed.status == "doing"


def _project_data() -> ProjectCreateData:
    return ProjectCreateData(name="Work", color=None)


def _create_data(
    *, project_id: int | None, status: str | None = None
) -> TaskCreateData:
    return TaskCreateData(
        title="Write tests",
        description="",
        status=status,
        project_id=project_id,
        due_date=None,
    )
