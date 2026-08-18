import pytest
from pydantic import ValidationError

from serializers.todo.task import TodoCreateInput, TodoProjectInput, TodoUpdateInput


def test_todo_create_strips_title_whitespace() -> None:
    task = TodoCreateInput.model_validate({"title": "  New task  "})

    assert task.title == "New task"


def test_todo_create_rejects_non_string_titles() -> None:
    with pytest.raises(ValidationError):
        TodoCreateInput.model_validate({"title": 123})


def test_todo_update_rejects_null_values() -> None:
    with pytest.raises(ValidationError):
        TodoUpdateInput.model_validate({"title": None})


def test_todo_update_treats_an_empty_due_date_as_unset() -> None:
    task = TodoUpdateInput.model_validate({"due_date": ""})

    assert task.due_date is None


def test_todo_create_treats_an_empty_due_date_as_unset() -> None:
    task = TodoCreateInput.model_validate({"title": "New task", "due_date": ""})

    assert task.due_date is None


def test_todo_project_treats_an_empty_project_id_as_unassigned() -> None:
    task = TodoProjectInput.model_validate({"project_id": ""})

    assert task.project_id is None
