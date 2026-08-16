import pytest
from asgiref.sync import async_to_sync
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from api.decorators import pydantic_body
from serializers.project.project import ProjectCreateInput


def test_pydantic_body_requires_a_pydantic_body_annotation() -> None:
    with pytest.raises(TypeError, match="Pydantic model"):

        @pydantic_body
        async def view(request: object, body: int) -> None: ...


def test_pydantic_body_requires_a_drf_request_argument() -> None:
    @pydantic_body
    async def view(request: object, body: ProjectCreateInput) -> Response:
        return Response({"name": body.name})

    with pytest.raises(TypeError, match="DRF Request"):
        async_to_sync(view)("not-a-request")  # type: ignore[call-arg]  # body is injected by pydantic_body


def test_pydantic_body_rejects_a_non_object_payload() -> None:
    @pydantic_body
    async def view(request: object, body: ProjectCreateInput) -> Response:
        return Response({"name": body.name})

    request = Request(
        APIRequestFactory().post("/", [], format="json"), parsers=[JSONParser()]
    )
    response = async_to_sync(view)(request)  # type: ignore[call-arg]  # body is injected by pydantic_body

    assert response.status_code == 400
    assert response.data["detail"] == "Expected a JSON object."


def test_pydantic_body_validates_and_injects_the_body() -> None:
    @pydantic_body
    async def view(request: object, body: ProjectCreateInput) -> Response:
        return Response({"name": body.name})

    request = Request(
        APIRequestFactory().post("/", {"name": "Launch"}, format="json"),
        parsers=[JSONParser()],
    )
    response = async_to_sync(view)(request)  # type: ignore[call-arg]  # body is injected by pydantic_body

    assert response.status_code == 200
    assert response.data["name"] == "Launch"


def test_pydantic_body_returns_validation_errors() -> None:
    @pydantic_body
    async def view(request: object, body: ProjectCreateInput) -> Response:
        return Response({"name": body.name})

    request = Request(
        APIRequestFactory().post("/", {"name": ""}, format="json"),
        parsers=[JSONParser()],
    )
    response = async_to_sync(view)(request)  # type: ignore[call-arg]  # body is injected by pydantic_body

    assert response.status_code == 400
    assert "name" in response.data["errors"]
