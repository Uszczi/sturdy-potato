from typing import Annotated

from adrf.decorators import api_view
from dependency_injector.wiring import Provide, inject
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from api.decorators import html_response
from config.auth import get_authenticated_user
from config.containers import Container
from infrastructure.repositories import ProjectRepository, TodoRepository


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@html_response
@inject
async def home_page(
    request: Request,
    repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    project_repository: Annotated[
        ProjectRepository, Provide[Container.project_repository]
    ],
) -> HttpResponse:
    user = get_authenticated_user(request)
    return render(
        request,
        "web/main.html",
        {
            "today": timezone.localdate(),
            "active_nav": "overview",
            "open_tasks": await repository.list_open_for_user(user, limit=5),
            "open_task_count": await repository.count_for_user(user, completed=False),
            "completed_task_count": await repository.count_for_user(
                user, completed=True
            ),
            "projects": await project_repository.list_for_user(user),
        },
    )
