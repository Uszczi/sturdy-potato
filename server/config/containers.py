from dependency_injector import containers, providers

from infrastructure.repositories import ProjectRepository, TodoRepository


class Container(containers.DeclarativeContainer):
    project_repository = providers.Factory(ProjectRepository)
    todo_repository = providers.Factory(TodoRepository)


container = Container()
