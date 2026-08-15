import pytest
from pydantic import ValidationError
from todo.serializers import TodoUpdateInput


def test_todo_update_rejects_null_values() -> None:
    with pytest.raises(ValidationError):
        TodoUpdateInput.model_validate({"title": None})
