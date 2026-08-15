from typing import cast

from rest_framework.request import Request

from .models import User


def get_authenticated_user(request: Request) -> User:
    return cast(User, request.user)
