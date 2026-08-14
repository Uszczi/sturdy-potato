from typing import cast

from infrastructure.repositories import TodoRepository
from potato.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import TodoSchema


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def task_list(request: Request) -> Response:
    user = cast(User, request.user)
    tasks = TodoRepository().list_for_user(user)
    return Response(TodoSchema(many=True).dump(tasks))
