from collections.abc import Mapping
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from infrastructure.models import Todo, User
from infrastructure.repositories import TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container

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
    user = get_authenticated_user(request)
    tasks = repository.list_for_user(user).order_by("completed", "-created_at")
    return render(request, "todo/task_list.html", {"tasks": tasks})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@inject
def task_create_page(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    if not isinstance(request.data, Mapping):
        return HttpResponseBadRequest("Invalid task title.")

    try:
        body = TodoCreateInput.model_validate({"title": request.data.get("title", "")})
    except PydanticValidationError:
        return HttpResponseBadRequest("Invalid task title.")

    user = get_authenticated_user(request)
    repository.create_for_user(user, body.model_dump())
    tasks = repository.list_for_user(user).order_by("completed", "-created_at")
    return render(request, "todo/_task_section.html", {"tasks": tasks})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@inject
def task_toggle_page(
    request: Request,
    task_id: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise Http404

    repository.update(task, {"completed": not task.completed})
    tasks = repository.list_for_user(user).order_by("completed", "-created_at")
    return render(request, "todo/_task_list.html", {"tasks": tasks})


def _parse_body(model: type[BaseModel], request: Request) -> BaseModel | Response:
    if not isinstance(request.data, dict):
        return Response(
            {"detail": "Expected a JSON object."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        return model.model_validate(request.data)
    except PydanticValidationError as error:
        return Response(
            {"errors": _format_validation_errors(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TodoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # noqa: RUF012

    @inject
    def list(
        self,
        request: Request,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        tasks = repository.list_for_user(user)
        return Response([_dump_task(task) for task in tasks])

    @inject
    def retrieve(
        self,
        request: Request,
        pk: int,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        task = _get_task_or_404(repository, user, pk)
        return Response(_dump_task(task))

    @inject
    def create(
        self,
        request: Request,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        body = _parse_body(TodoCreateInput, request)
        if isinstance(body, Response):
            return body

        user = get_authenticated_user(request)
        task = repository.create_for_user(user, body.model_dump())
        return Response(_dump_task(task), status=status.HTTP_201_CREATED)

    @inject
    def partial_update(
        self,
        request: Request,
        pk: int,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        body = _parse_body(TodoUpdateInput, request)
        if isinstance(body, Response):
            return body

        user = get_authenticated_user(request)
        task = _get_task_or_404(repository, user, pk)
        task = repository.update(task, body.model_dump(exclude_unset=True))
        return Response(_dump_task(task))

    @inject
    def destroy(
        self,
        request: Request,
        pk: int,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        task = _get_task_or_404(repository, user, pk)
        repository.delete(task)
        return Response(status=status.HTTP_204_NO_CONTENT)
