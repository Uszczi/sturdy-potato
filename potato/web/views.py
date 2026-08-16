from typing import Annotated

from dependency_injector.wiring import Provide, inject
from django.http import HttpResponse
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.decorators import html_response, pydantic_body
from infrastructure.models import Todo, User
from infrastructure.repositories import ProjectRepository, TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container
from serializers.project.project import ProjectCreateInput
from serializers.todo.task import TodoCreateInput, TodoProjectInput


def _get_task_or_404(
    repository: TodoRepository,
    user: User,
    task_id: int,
) -> Todo:
    task = repository.get_for_user(user, task_id)
    if task is None:
        raise NotFound("Not found.")
    return task


def _resolve_task_project(
    repository: TodoRepository,
    user: User,
    data: dict[str, object],
) -> dict[str, object]:
    if "project_id" not in data:
        return data

    project_id = data.pop("project_id")
    if project_id is None:
        data["project"] = None
        return data

    if not isinstance(project_id, int):
        raise NotFound("Project not found.")
    project = repository.get_project_for_user(user, project_id)
    if project is None:
        raise NotFound("Project not found.")
    data["project"] = project
    return data


def _task_context(
    repository: TodoRepository,
    project_repository: ProjectRepository,
    user: User,
) -> dict[str, object]:
    return {
        "tasks": repository.list_for_user(user).order_by("completed", "-created_at"),
        "projects": project_repository.list_for_user(user),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@html_response
@inject
def task_list_page(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    project_repository: Annotated[
        ProjectRepository, Provide[Container.project_repository]
    ],
) -> HttpResponse:
    user = get_authenticated_user(request)
    return render(
        request,
        "todo/task_list.html",
        _task_context(repository, project_repository, user),
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@html_response
@pydantic_body
@inject
def task_create_page(
    request: Request,
    body: TodoCreateInput,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    project_repository: Annotated[
        ProjectRepository, Provide[Container.project_repository]
    ],
) -> HttpResponse:
    user = get_authenticated_user(request)
    data = _resolve_task_project(repository, user, body.model_dump())
    repository.create_for_user(user, data)
    return render(
        request,
        "todo/_task_section.html",
        _task_context(repository, project_repository, user),
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@html_response
@extend_schema(request=None)
@inject
def task_toggle_page(
    request: Request,
    pk: int,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    project_repository: Annotated[
        ProjectRepository, Provide[Container.project_repository]
    ],
) -> HttpResponse:
    user = get_authenticated_user(request)
    task = _get_task_or_404(repository, user, pk)

    repository.update(task, {"completed": not task.completed})
    return render(
        request,
        "todo/_task_list.html",
        _task_context(repository, project_repository, user),
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@html_response
@pydantic_body
@inject
def task_assign_project_page(
    request: Request,
    pk: int,
    body: TodoProjectInput,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    project_repository: Annotated[
        ProjectRepository, Provide[Container.project_repository]
    ],
) -> HttpResponse:
    user = get_authenticated_user(request)
    task = _get_task_or_404(repository, user, pk)
    data = _resolve_task_project(repository, user, body.model_dump())
    repository.update(task, data)
    return render(
        request,
        "todo/_task_section.html",
        _task_context(repository, project_repository, user),
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@html_response
@inject
def project_list_page(
    request: Request,
    repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    return render(
        request,
        "projects/project_list.html",
        {"projects": repository.list_for_user(user)},
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@html_response
@pydantic_body
@inject
def project_create_page(
    request: Request,
    body: ProjectCreateInput,
    repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    if repository.list_for_user(user).filter(name=body.name).exists():
        return Response(
            {"errors": {"name": ["A project with this name already exists."]}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    repository.create_for_user(user, body.model_dump())
    return render(
        request,
        "projects/_project_section.html",
        {"projects": repository.list_for_user(user)},
    )
