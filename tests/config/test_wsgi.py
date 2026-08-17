from django.core.handlers.wsgi import WSGIHandler

from config.wsgi import application


def test_wsgi_application_is_a_wsgi_handler() -> None:
    assert isinstance(application, WSGIHandler)
