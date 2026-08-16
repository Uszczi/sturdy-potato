import pytest

from api.decorators import pydantic_body
from serializers.project.project import ProjectCreateInput


def test_pydantic_body_requires_a_pydantic_body_annotation() -> None:
    with pytest.raises(TypeError, match="Pydantic model"):

        @pydantic_body
        def view(request: object, body: int) -> None: ...


def test_pydantic_body_requires_a_drf_request_argument() -> None:
    @pydantic_body
    def view(request: object, body: ProjectCreateInput) -> None: ...

    with pytest.raises(TypeError, match="DRF Request"):
        view("not-a-request")
