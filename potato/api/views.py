from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from infrastructure.models import Todo, User
from infrastructure.repositories import TodoRepository
from potato.auth import get_authenticated_user
from potato.containers import Container
from serializers.todo.task import TodoCreateInput, TodoSchema, TodoUpdateInput

from .decorators import pydantic_body, pydantic_response


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
        return Response([_dump_task(task) for task in tasks])

    @pydantic_response(TodoSchema)
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

    @pydantic_response(TodoSchema, status_code=status.HTTP_201_CREATED)
    @pydantic_body
    @inject
    def create(
        self,
        request: Request,
        body: TodoCreateInput,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        task = repository.create_for_user(user, body.model_dump())
        return Response(_dump_task(task), status=status.HTTP_201_CREATED)

    @pydantic_response(TodoSchema)
    @pydantic_body
    @inject
    def partial_update(
        self,
        request: Request,
        pk: int,
        body: TodoUpdateInput,
        repository: Annotated[TodoRepository, Provide[Container.todo_repository]],
    ) -> Response:
        user = get_authenticated_user(request)
        task = _get_task_or_404(repository, user, pk)
        task = repository.update(task, body.model_dump(exclude_unset=True))
        return Response(_dump_task(task))

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
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
