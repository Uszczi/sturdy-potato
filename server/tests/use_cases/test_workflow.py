import pytest

from use_cases.exceptions import InvalidWorkflow, UnknownStatus
from use_cases.workflow import (
    DEFAULT_WORKFLOW,
    MAX_STATUSES,
    Status,
    StatusAssignment,
    Workflow,
)


def _workflow(*statuses: Status) -> Workflow:
    return Workflow(statuses)


TODO = Status(key="todo", label="Todo", is_initial=True)
DOING = Status(key="doing", label="Doing")
SHIPPED = Status(key="shipped", label="Shipped", is_terminal=True)
CANCELLED = Status(key="cancelled", label="Cancelled", is_terminal=True)


def test_default_workflow_is_open_then_done() -> None:
    assert [s.key for s in DEFAULT_WORKFLOW.statuses] == ["open", "done"]
    assert DEFAULT_WORKFLOW.initial.key == "open"
    assert DEFAULT_WORKFLOW.first_terminal.key == "done"


def test_keys_follow_declaration_order() -> None:
    workflow = _workflow(TODO, DOING, SHIPPED)

    assert workflow.keys == ("todo", "doing", "shipped")


def test_rejects_fewer_than_two_statuses() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(Status(key="only", label="Only", is_initial=True, is_terminal=True))


def test_rejects_more_than_the_maximum() -> None:
    many = [Status(key=f"s{n}", label=f"S{n}") for n in range(MAX_STATUSES)]
    many[0] = Status(key="s0", label="S0", is_initial=True)
    many[1] = Status(key="s1", label="S1", is_terminal=True)

    with pytest.raises(InvalidWorkflow):
        _workflow(*many, Status(key="extra", label="Extra"))


def test_allows_exactly_the_maximum() -> None:
    many = [Status(key=f"s{n}", label=f"S{n}") for n in range(MAX_STATUSES)]
    many[0] = Status(key="s0", label="S0", is_initial=True)
    many[-1] = Status(key=f"s{MAX_STATUSES - 1}", label="Last", is_terminal=True)

    assert len(_workflow(*many).statuses) == MAX_STATUSES


def test_rejects_duplicate_keys() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(TODO, Status(key="todo", label="Todo again", is_terminal=True))


def test_rejects_no_initial_status() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(Status(key="doing", label="Doing"), SHIPPED)


def test_rejects_two_initial_statuses() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(TODO, Status(key="doing", label="Doing", is_initial=True), SHIPPED)


def test_rejects_no_terminal_status() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(TODO, DOING)


def test_allows_several_terminal_statuses() -> None:
    workflow = _workflow(TODO, SHIPPED, CANCELLED)

    assert workflow.first_terminal.key == "shipped"
    assert workflow.is_terminal("cancelled")


def test_rejects_an_initial_status_that_is_also_terminal() -> None:
    # A task would be born done, which is a bug rather than a workflow.
    with pytest.raises(InvalidWorkflow, match="cannot also be terminal"):
        _workflow(
            Status(key="todo", label="Todo", is_initial=True, is_terminal=True), SHIPPED
        )


def test_rejects_a_malformed_key() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(Status(key="In Review", label="In Review", is_initial=True), SHIPPED)


def test_rejects_a_blank_label() -> None:
    with pytest.raises(InvalidWorkflow):
        _workflow(Status(key="todo", label="  ", is_initial=True), SHIPPED)


def test_assign_pairs_a_key_with_its_done_ness() -> None:
    workflow = _workflow(TODO, DOING, SHIPPED)

    assert workflow.assign("doing") == StatusAssignment(key="doing", is_done=False)
    assert workflow.assign("shipped") == StatusAssignment(key="shipped", is_done=True)


def test_assign_rejects_a_status_outside_the_workflow() -> None:
    with pytest.raises(UnknownStatus):
        _workflow(TODO, SHIPPED).assign("review")


def test_assign_initial_starts_a_task_off_undone() -> None:
    assert _workflow(TODO, SHIPPED).assign_initial() == StatusAssignment(
        key="todo", is_done=False
    )


def test_as_changes_writes_status_and_done_ness_together() -> None:
    # The denormalised is_done must never be written without its status.
    assert StatusAssignment(key="shipped", is_done=True).as_changes() == {
        "status": "shipped",
        "is_done": True,
    }


def test_adopt_keeps_a_status_the_workflow_already_has() -> None:
    workflow = _workflow(TODO, DOING, SHIPPED)

    assert workflow.adopt("doing", is_done=False) == StatusAssignment(
        key="doing", is_done=False
    )


def test_adopt_recomputes_done_ness_for_a_shared_key() -> None:
    # "doing" is terminal here but was not in the workflow the task came from.
    workflow = _workflow(TODO, Status(key="doing", label="Doing", is_terminal=True))

    assert workflow.adopt("doing", is_done=False) == StatusAssignment(
        key="doing", is_done=True
    )


def test_adopt_maps_an_unknown_open_status_to_the_initial() -> None:
    workflow = _workflow(TODO, SHIPPED)

    assert workflow.adopt("review", is_done=False) == StatusAssignment(
        key="todo", is_done=False
    )


def test_adopt_maps_an_unknown_done_status_to_the_first_terminal() -> None:
    workflow = _workflow(TODO, SHIPPED, CANCELLED)

    assert workflow.adopt("archived", is_done=True) == StatusAssignment(
        key="shipped", is_done=True
    )


def test_round_trips_through_its_stored_form() -> None:
    workflow = _workflow(TODO, DOING, SHIPPED)

    assert Workflow.from_dicts(workflow.to_dicts()) == workflow


def test_stored_form_keeps_declaration_order() -> None:
    stored = _workflow(TODO, DOING, SHIPPED).to_dicts()

    assert [entry["key"] for entry in stored] == ["todo", "doing", "shipped"]
    assert stored[0] == {
        "key": "todo",
        "label": "Todo",
        "is_initial": True,
        "is_terminal": False,
    }
