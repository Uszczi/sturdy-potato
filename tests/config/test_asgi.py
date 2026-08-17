from django.core.handlers.asgi import ASGIHandler

from config.asgi import application


def test_asgi_application_is_an_asgi_handler() -> None:
    assert isinstance(application, ASGIHandler)
