from typing import Annotated

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from infrastructure.models import Project, User
from infrastructure.repositories import ProjectRepository, TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container
from potato.repository_helpers import (
    dump_project,
    dump_task,
    get_project_or_404,
    resolve_project,
    get_task_or_404,
)
from serializers.order import ReorderInput
from serializers.project.project import (
    ProjectCreateInput,
    ProjectSchema,
    ProjectUpdateInput,
)
from serializers.todo.task import (
    TodoCreateInput,
    TodoSchema,
    TodoUpdateInput,
)

from .decorators import pydantic_body, pydantic_response


class TodoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # noqa: RUF012

    @pydantic_response(TodoSchema)
    @inject
    def list(
        self,
        request: Request,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        tasks = repository.list_for_user(user)
        return Response([dump_task(task) for task in tasks])

    @action(detail=False, methods=["post"], url_path="reorder")
    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    @pydantic_body
    @inject
    def reorder(
        self,
        request: Request,
        body: ReorderInput,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        if not repository.reorder_for_user(user, body.order):
            return Response(
                {"detail": "Order contains tasks outside this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @pydantic_response(TodoSchema)
    @inject
    def retrieve(
        self,
        request: Request,
        pk: int,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        task = get_task_or_404(repository, user, pk)
        return Response(dump_task(task))

    @pydantic_response(TodoSchema, status_code=status.HTTP_201_CREATED)
    @pydantic_body
    @inject
    def create(
        self,
        request: Request,
        body: TodoCreateInput,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
        project_repository: Annotated[
            ProjectRepository, Provide[Container.project_repository]
        ],
    ) -> Response:
        user = get_authenticated_user(request)
        data = resolve_project(project_repository, user, body.model_dump())
        task = repository.create_for_user(user, data)
        return Response(dump_task(task), status=status.HTTP_201_CREATED)

    @pydantic_response(TodoSchema)
    @pydantic_body
    @inject
    def partial_update(
        self,
        request: Request,
        pk: int,
        body: TodoUpdateInput,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
        project_repository: Annotated[
            ProjectRepository, Provide[Container.project_repository]
        ],
    ) -> Response:
        user = get_authenticated_user(request)
        task = get_task_or_404(repository, user, pk)
        data = resolve_project(
            project_repository,
            user,
            body.model_dump(exclude_unset=True),
        )
        task = repository.update(task, data)
        return Response(dump_task(task))

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    @inject
    def destroy(
        self,
        request: Request,
        pk: int,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        task = get_task_or_404(repository, user, pk)
        repository.delete(task)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # noqa: RUF012

    @pydantic_response(ProjectSchema)
    @inject
    def list(
        self,
        request: Request,
        repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        projects = repository.list_for_user(user)
        return Response([dump_project(project) for project in projects])

    @action(detail=False, methods=["post"], url_path="reorder")
    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    @pydantic_body
    @inject
    def reorder(
        self,
        request: Request,
        body: ReorderInput,
        repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        if not repository.reorder_for_user(user, body.order):
            return Response(
                {"detail": "Order contains projects outside this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @pydantic_response(ProjectSchema)
    @inject
    def retrieve(
        self,
        request: Request,
        pk: int,
        repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        return Response(dump_project(get_project_or_404(repository, user, pk)))

    @pydantic_response(ProjectSchema, status_code=status.HTTP_201_CREATED)
    @pydantic_body
    @inject
    def create(
        self,
        request: Request,
        body: ProjectCreateInput,
        repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        if repository.list_for_user(user).filter(name=body.name).exists():
            return Response(
                {"errors": {"name": ["A project with this name already exists."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project = repository.create_for_user(user, body.model_dump())
        return Response(dump_project(project), status=status.HTTP_201_CREATED)

    @pydantic_response(ProjectSchema)
    @pydantic_body
    @inject
    def partial_update(
        self,
        request: Request,
        pk: int,
        body: ProjectUpdateInput,
        repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        project = get_project_or_404(repository, user, pk)
        data = body.model_dump(exclude_unset=True)
        if (
            "name" in data
            and repository.list_for_user(user)
            .exclude(id=project.id)
            .filter(name=data["name"])
            .exists()
        ):
            return Response(
                {"errors": {"name": ["A project with this name already exists."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project = repository.update(project, data)
        return Response(dump_project(project))

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    @inject
    def destroy(
        self,
        request: Request,
        pk: int,
        repository: Annotated[ProjectRepository, Provide[Container.project_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        project = get_project_or_404(repository, user, pk)
        repository.delete(project)
        return Response(status=status.HTTP_204_NO_CONTENT)
