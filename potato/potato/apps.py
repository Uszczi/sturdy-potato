from django.apps import AppConfig


class PotatoConfig(AppConfig):
    name = "potato"

    def ready(self) -> None:
        from .containers import container

        container.wire(modules=["todo.views"])
