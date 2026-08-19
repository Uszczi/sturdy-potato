class UseCaseError(Exception):
    status_code = 400
    detail = "Error."

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(UseCaseError):
    status_code = 404
    detail = "Not found."


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
