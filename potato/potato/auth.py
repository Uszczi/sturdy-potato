from typing import cast

from django.http import HttpRequest
from rest_framework.request import Request

from infrastructure.models import User


def get_authenticated_user(request: HttpRequest | Request) -> User:
    return cast(User, request.user)
