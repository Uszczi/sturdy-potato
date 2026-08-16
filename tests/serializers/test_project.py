import pytest
from pydantic import ValidationError

from serializers.project.project import ProjectCreateInput, ProjectUpdateInput


def test_project_create_strips_name_whitespace() -> None:
    project = ProjectCreateInput.model_validate({"name": "  Launch  "})

    assert project.name == "Launch"


def test_project_create_rejects_non_string_names() -> None:
    with pytest.raises(ValidationError):
        ProjectCreateInput.model_validate({"name": 123})


def test_project_update_strips_name_whitespace() -> None:
    project = ProjectUpdateInput.model_validate({"name": "  Launch  "})

    assert project.name == "Launch"


def test_project_update_rejects_null_names() -> None:
    with pytest.raises(ValidationError):
        ProjectUpdateInput.model_validate({"name": None})


def test_project_update_rejects_non_string_names() -> None:
    with pytest.raises(ValidationError):
        ProjectUpdateInput.model_validate({"name": 123})
