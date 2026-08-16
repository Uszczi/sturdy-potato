from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, cast, get_type_hints

from django.http import QueryDict
from drf_spectacular.utils import OpenApiRequest, extend_schema
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


def _format_validation_errors(
    error: PydanticValidationError,
) -> dict[str, list[str]]:
    messages: dict[str, list[str]] = {}
    for detail in error.errors():
        field = ".".join(str(part) for part in detail["loc"]) or "non_field_errors"
        messages.setdefault(field, []).append(detail["msg"])
    return messages


def _get_request_data(request: Request) -> dict[str, object] | None:
    data: dict[str, object]
    if isinstance(request.data, QueryDict):
        data = {key: value for key, value in request.data.items()}
    elif isinstance(request.data, Mapping):
        data = cast(dict[str, object], dict(request.data))
    else:
        return None

    data.pop("csrfmiddlewaretoken", None)
    return data


def pydantic_body[**P, R](view: Callable[P, R]) -> Callable[P, R]:
    """Validate a request body, inject the model, and expose its OpenAPI schema."""

    body_model = get_type_hints(view).get("body")
    if not isinstance(body_model, type) or not issubclass(body_model, BaseModel):
        raise TypeError(
            "pydantic_body requires a body argument annotated with a Pydantic model"
        )

    @wraps(view)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        request = kwargs.get("request")
        if request is None:
            request = args[1] if len(args) > 1 else args[0]
        if not isinstance(request, Request):
            raise TypeError("pydantic_body requires a DRF Request argument")

        data = _get_request_data(request)
        if data is None:
            return cast(
                R,
                Response(
                    {"detail": "Expected a JSON object."},
                    status=status.HTTP_400_BAD_REQUEST,
                ),
            )

        try:
            body = body_model.model_validate(data)
        except PydanticValidationError as error:
            return cast(
                R,
                Response(
                    {"errors": _format_validation_errors(error)},
                    status=status.HTTP_400_BAD_REQUEST,
                ),
            )

        return cast(Callable[..., R], view)(*args, body=body, **kwargs)

    annotated_view = cast(
        Any,
        extend_schema(request=OpenApiRequest(body_model.model_json_schema()))(wrapped),
    )
    annotated_view.schema = annotated_view.kwargs["schema"]()
    return cast(Callable[P, R], annotated_view)
