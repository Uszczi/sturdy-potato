from dependency_injector import containers, providers
from infrastructure.repositories import TodoRepository


class Container(containers.DeclarativeContainer):
    todo_repository = providers.Factory(TodoRepository)


container = Container()
