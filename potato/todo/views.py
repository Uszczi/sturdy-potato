from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any, cast

from dependency_injector.wiring import Provide, inject
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from infrastructure.models import Todo
from infrastructure.repositories import TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container
from potato.models import User

from .serializers import TodoCreateInput, TodoSchema, TodoUpdateInput


def _format_validation_errors(
    error: PydanticValidationError,
) -> dict[str, list[str]]:
    messages: dict[str, list[str]] = {}
    for detail in error.errors():
        field = ".".join(str(part) for part in detail["loc"]) or "non_field_errors"
        messages.setdefault(field, []).append(detail["msg"])
    return messages


def _dump_task(task: Todo) -> dict[str, Any]:
    return TodoSchema.model_validate(task).model_dump(mode="json")


def _get_task_or_404(
    repository: TodoRepository,
    user: User,
    task_id: int,
) -> Todo:
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")
    return task


@login_required
@inject
def task_list_page(
    request: HttpRequest,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    user = cast(User, request.user)
    tasks = repository.list_for_user(user)
    return render(request, "todo/task_list.html", {"tasks": tasks})


def validate_body(
    model: type[BaseModel],
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    def decorator(view: Callable[..., Response]) -> Callable[..., Response]:
        @wraps(view)
        def wrapped(request: Request, *args: Any, **kwargs: Any) -> Response:
            if not isinstance(request.data, dict):
                raise DRFValidationError(
                    {"detail": "Expected a JSON object."},
                )

            try:
                body = model.model_validate(request.data)
            except PydanticValidationError as error:
                raise DRFValidationError(
                    {"errors": _format_validation_errors(error)},
                ) from error
            return view(request, *args, body=body, **kwargs)

        return wrapped

    return decorator


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@inject
def task_list(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    tasks = repository.list_for_user(user)
    return Response([_dump_task(task) for task in tasks])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@inject
def task_detail(
    request: Request,
    task_id: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    task = _get_task_or_404(repository, user, task_id)

    return Response(_dump_task(task))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@validate_body(TodoCreateInput)
@inject
def task_create(
    request: Request,
    body: TodoCreateInput,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)

    task = repository.create_for_user(user, body.model_dump())
    return Response(
        _dump_task(task),
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@validate_body(TodoUpdateInput)
@inject
def task_update(
    request: Request,
    task_id: int,
    body: TodoUpdateInput,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    task = _get_task_or_404(repository, user, task_id)

    task = repository.update(task, body.model_dump(exclude_unset=True))
    return Response(_dump_task(task))


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@inject
def task_delete(
    request: Request,
    task_id: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> Response:
    user = get_authenticated_user(request)
    task = _get_task_or_404(repository, user, task_id)

    repository.delete(task)
    return Response(status=status.HTTP_204_NO_CONTENT)
