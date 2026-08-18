from django.apps import AppConfig


class ConfigConfig(AppConfig):
    name = "config"

    def ready(self) -> None:
        from .containers import container

        container.wire(modules=["api.views"])
