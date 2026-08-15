from infrastructure.models import Todo


def test_todo_string_representation() -> None:
    assert str(Todo(title="Task")) == "Task"
