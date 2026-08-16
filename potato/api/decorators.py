from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, cast, get_type_hints

from django.http import QueryDict
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiRequest, OpenApiResponse, extend_schema
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

    def _resolve_body(
        args: tuple[object, ...],
        kwargs: dict[str, object],
    ) -> tuple[BaseModel | None, Response | None]:
        request = kwargs.get("request")
        if request is None:
            request = args[1] if len(args) > 1 else args[0]
        if not isinstance(request, Request):
            raise TypeError("pydantic_body requires a DRF Request argument")

        data = _get_request_data(request)
        if data is None:
            return None, Response(
                {"detail": "Expected a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return body_model.model_validate(data), None
        except PydanticValidationError as error:
            return None, Response(
                {"errors": _format_validation_errors(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @wraps(view)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        body, error_response = _resolve_body(args, kwargs)
        if error_response is not None:
            return cast(R, error_response)
        result = await cast(Callable[..., Any], view)(*args, body=body, **kwargs)
        return cast(R, result)

    annotated_view = cast(
        Any,
        extend_schema(request=OpenApiRequest(body_model.model_json_schema()))(wrapped),
    )
    annotated_view.schema = annotated_view.kwargs["schema"]()
    return cast(Callable[P, R], annotated_view)


def pydantic_response[**P, R](
    model: type[BaseModel],
    *,
    status_code: int = status.HTTP_200_OK,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Expose a Pydantic response model through the OpenAPI schema."""

    response_schema: dict[str, object] = model.model_json_schema(mode="serialization")

    def decorator(view: Callable[P, R]) -> Callable[P, R]:
        annotated_view = cast(
            Any,
            extend_schema(responses={status_code: response_schema})(view),
        )
        annotated_view.schema = annotated_view.kwargs["schema"]()
        return cast(Callable[P, R], annotated_view)

    return decorator


def html_response[**P, R](view: Callable[P, R]) -> Callable[P, R]:
    """Declare a function-based view response as HTML in OpenAPI."""

    annotated_view = cast(
        Any,
        extend_schema(
            responses={
                (status.HTTP_200_OK, "text/html"): OpenApiResponse(
                    response=OpenApiTypes.STR,
                )
            }
        )(view),
    )
    annotated_view.schema = annotated_view.kwargs["schema"]()
    return cast(Callable[P, R], annotated_view)
