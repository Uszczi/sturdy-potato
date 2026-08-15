import pytest
from pydantic import ValidationError
from todo.serializers import TodoCreateInput, TodoUpdateInput


def test_todo_create_strips_title_whitespace() -> None:
    task = TodoCreateInput.model_validate({"title": "  New task  "})

    assert task.title == "New task"


def test_todo_create_rejects_non_string_titles() -> None:
    with pytest.raises(ValidationError):
        TodoCreateInput.model_validate({"title": 123})


def test_todo_update_rejects_null_values() -> None:
    with pytest.raises(ValidationError):
        TodoUpdateInput.model_validate({"title": None})
