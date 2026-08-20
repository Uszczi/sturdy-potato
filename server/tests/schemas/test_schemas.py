from datetime import date

import pytest
from pydantic import ValidationError

from schemas.order import ReorderInput
from schemas.project import ProjectCreateInput, ProjectUpdateInput
from schemas.task import TaskCreateInput, TaskUpdateInput


def test_todo_create_strips_title_and_blanks_optionals() -> None:
    model = TaskCreateInput(title="  Buy milk  ", project_id="", due_date="")

    assert model.title == "Buy milk"
    assert model.project_id is None
    assert model.due_date is None


def test_todo_create_keeps_provided_optionals() -> None:
    model = TaskCreateInput(title="x", project_id=3, due_date="2024-01-02")

    assert model.project_id == 3
    assert model.due_date == date(2024, 1, 2)


def test_todo_create_rejects_a_non_string_title() -> None:
    with pytest.raises(ValidationError):
        TaskCreateInput(title=123)


def test_todo_create_rejects_a_blank_title() -> None:
    with pytest.raises(ValidationError):
        TaskCreateInput(title="   ")


@pytest.mark.parametrize("field", ["title", "description", "status"])
def test_todo_update_rejects_null_fields(field: str) -> None:
    with pytest.raises(ValidationError):
        TaskUpdateInput(**{field: None})


def test_todo_update_blanks_and_keeps_optionals() -> None:
    blanked = TaskUpdateInput(project_id="", due_date="")
    assert blanked.project_id is None
    assert blanked.due_date is None

    kept = TaskUpdateInput(project_id=2, due_date="2024-01-02")
    assert kept.project_id == 2
    assert kept.due_date == date(2024, 1, 2)


def test_project_create_strips_name() -> None:
    assert ProjectCreateInput(name="  Roadmap  ").name == "Roadmap"


def test_project_create_rejects_a_non_string_name() -> None:
    with pytest.raises(ValidationError):
        ProjectCreateInput(name=123)


def test_project_update_rejects_null_name() -> None:
    with pytest.raises(ValidationError):
        ProjectUpdateInput(name=None)


def test_project_update_strips_name() -> None:
    assert ProjectUpdateInput(name="  New  ").name == "New"


def test_project_update_rejects_a_non_string_name() -> None:
    with pytest.raises(ValidationError):
        ProjectUpdateInput(name=123)


def test_reorder_accepts_unique_ids() -> None:
    assert ReorderInput(order=[3, 1, 2]).order == [3, 1, 2]


def test_reorder_rejects_duplicate_ids() -> None:
    with pytest.raises(ValidationError):
        ReorderInput(order=[1, 1])
