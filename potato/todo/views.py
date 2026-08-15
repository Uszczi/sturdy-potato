from typing import Annotated, Any, cast

from dependency_injector.wiring import Provide, inject
from infrastructure.repositories import TodoRepository
from marshmallow import ValidationError
from potato.auth import get_authenticated_user
from potato.containers import Container
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import TodoSchema


def _load_task_data(
    request: Request,
    *,
    partial: bool,
) -> dict[str, Any] | Response:
    if not isinstance(request.data, dict):
        return Response(
            {"detail": "Expected a JSON object."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        return cast(dict[str, Any], TodoSchema().load(request.data, partial=partial))
    except ValidationError as error:
        return Response(
            {"errors": error.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@inject
def task_list(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    tasks = repository.list_for_user(user)
    return Response(TodoSchema(many=True).dump(tasks))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@inject
def task_detail(
    request: Request,
    task_id: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")

    return Response(TodoSchema().dump(task))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@inject
def task_create(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    data = _load_task_data(request, partial=False)
    if isinstance(data, Response):
        return data

    task = repository.create_for_user(user, data)
    return Response(
        TodoSchema().dump(task),
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@inject
def task_update(
    request: Request,
    task_id: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")

    data = _load_task_data(request, partial=True)
    if isinstance(data, Response):
        return data

    task = repository.update(task, data)
    return Response(TodoSchema().dump(task))


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@inject
def task_delete(
    request: Request,
    task_id: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")

    repository.delete(task)
    return Response(status=status.HTTP_204_NO_CONTENT)
