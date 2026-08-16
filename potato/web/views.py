from typing import Annotated

from dependency_injector.wiring import Provide, inject
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.decorators import html_response, pydantic_body
from infrastructure.models import Project, Todo, User
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


def _get_project_or_404(
    repository: ProjectRepository,
    user: User,
    project_id: int,
) -> Project:
    project = repository.get_for_user(user, project_id)
    if project is None:
        raise NotFound("Project not found.")
    return project


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
    view: str = "inbox",
    project: Project | None = None,
) -> dict[str, object]:
    tasks = repository.list_for_user(user)
    if project is not None:
        tasks = tasks.filter(project=project)
    elif view == "inbox":
        tasks = tasks.filter(project__isnull=True)
    elif view == "today":
        tasks = tasks.filter(due_date=timezone.localdate())
    elif view == "upcoming":
        tasks = tasks.filter(
            due_date__gt=timezone.localdate(),
            completed=False,
        )
    return {
        "active_nav": view,
        "active_project_id": project.id if project else None,
        "project": project,
        "task_query": (
            f"?project={project.id}"
            if project
            else f"?view={view}" if view != "inbox" else ""
        ),
        "task_view": view,
        "tasks": tasks.order_by(
            "position", "completed", "due_date", "-created_at", "-id"
        ),
        "projects": project_repository.list_for_user(user),
    }


def _task_view(request: Request) -> str:
    view = request.query_params.get("view", "inbox")
    return view if view in {"inbox", "today", "upcoming"} else "inbox"


def _task_scope(
    request: Request,
    project_repository: ProjectRepository,
    user: User,
) -> tuple[str, Project | None]:
    project_id = request.query_params.get("project")
    if project_id is None:
        return _task_view(request), None

    try:
        project_pk = int(project_id)
    except ValueError as error:
        raise NotFound("Project not found.") from error
    return "project", _get_project_or_404(project_repository, user, project_pk)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@html_response
@inject
def home_page(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    project_repository: Annotated[
        ProjectRepository, Provide[Container.project_repository]
    ],
) -> HttpResponse:
    user = get_authenticated_user(request)
    tasks = repository.list_for_user(user)
    projects = project_repository.list_for_user(user)
    return render(
        request,
        "web/main.html",
        {
            "today": timezone.localdate(),
            "active_nav": "overview",
            "open_tasks": tasks.filter(completed=False)[:5],
            "open_task_count": tasks.filter(completed=False).count(),
            "completed_task_count": tasks.filter(completed=True).count(),
            "projects": projects,
        },
    )


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
    view, project = _task_scope(request, project_repository, user)
    return render(
        request,
        "todo/task_list.html",
        _task_context(repository, project_repository, user, view, project),
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
    view, project = _task_scope(request, project_repository, user)
    data = _resolve_task_project(repository, user, body.model_dump())
    repository.create_for_user(user, data)
    return render(
        request,
        "todo/_task_section.html",
        _task_context(repository, project_repository, user, view, project),
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
    view, project = _task_scope(request, project_repository, user)
    task = _get_task_or_404(repository, user, pk)

    repository.update(task, {"completed": not task.completed})
    return render(
        request,
        "todo/_task_list.html",
        _task_context(repository, project_repository, user, view, project),
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
    view, project = _task_scope(request, project_repository, user)
    task = _get_task_or_404(repository, user, pk)
    data = _resolve_task_project(repository, user, body.model_dump())
    repository.update(task, data)
    return render(
        request,
        "todo/_task_section.html",
        _task_context(repository, project_repository, user, view, project),
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
        {
            "active_nav": "projects",
            "projects": repository.list_for_user(user),
        },
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@html_response
@inject
def project_detail_page(
    request: Request,
    pk: int,
    repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    todo_repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
) -> HttpResponse:
    user = get_authenticated_user(request)
    project = _get_project_or_404(repository, user, pk)
    return render(
        request,
        "todo/task_list.html",
        _task_context(todo_repository, repository, user, "project", project),
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
