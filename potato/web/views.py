from typing import Annotated

from dependency_injector.wiring import Provide, inject
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from api.decorators import pydantic_body
from infrastructure.repositories import TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container
from serializers.todo.task import TodoCreateInput

from rest_framework.exceptions import NotFound
from infrastructure.models import Todo, User


def _get_task_or_404(
    repository: TodoRepository,
    user: User,
    task_id: int,
) -> Todo:
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")
    return task


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@inject
def task_list_page(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    tasks = repository.list_for_user(user).order_by("completed", "-created_at")
    return render(request, "todo/task_list.html", {"tasks": tasks})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@pydantic_body
@inject
def task_create_page(
    request: Request,
    body: TodoCreateInput,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    repository.create_for_user(user, body.model_dump())
    tasks = repository.list_for_user(user).order_by("completed", "-created_at")
    return render(request, "todo/_task_section.html", {"tasks": tasks})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@inject
def task_toggle_page(
    request: Request,
    pk: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    task = _get_task_or_404(repository, user, pk)

    repository.update(task, {"completed": not task.completed})
    tasks = repository.list_for_user(user).order_by("completed", "-created_at")
    return render(request, "todo/_task_list.html", {"tasks": tasks})
