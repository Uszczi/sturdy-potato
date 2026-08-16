from infrastructure.models import Project, Todo


def test_todo_string_representation() -> None:
    assert str(Todo(title="Task")) == "Task"


def test_project_string_representation() -> None:
    assert str(Project(name="Launch")) == "Launch"
