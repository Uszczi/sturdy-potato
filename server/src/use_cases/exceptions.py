from typing import ClassVar


class UseCaseError(Exception):
    status_code = 400
    detail = "Error."
    # Extra HTTP headers to attach when this error is mapped to a response.
    headers: ClassVar[dict[str, str] | None] = None

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(UseCaseError):
    status_code = 404
    detail = "Not found."


class AuthenticationError(UseCaseError):
    status_code = 401
    detail = "Not authenticated."
    headers: ClassVar[dict[str, str] | None] = {"WWW-Authenticate": "Bearer"}


class InvalidCredentials(AuthenticationError):
    detail = "No active account found with the given credentials."


class InvalidToken(AuthenticationError):
    detail = "Invalid or expired token."


class ConflictError(UseCaseError):
    status_code = 400
    detail = "Conflict."


class TaskNotFound(NotFoundError):
    detail = "Not found."


class ProjectNotFound(NotFoundError):
    detail = "Project not found."


class ProjectNameConflict(ConflictError):
    detail = "A project with this name already exists."


class InvalidReorder(UseCaseError):
    status_code = 400
    detail = "Order contains items outside this user."


class InvalidTimezone(UseCaseError):
    status_code = 400
    detail = "Unknown time zone."
