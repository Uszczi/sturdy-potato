from collections.abc import Mapping
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from pydantic import ValidationError as PydanticValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from infrastructure.repositories import TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container
from todo.serializers import TodoCreateInput


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
