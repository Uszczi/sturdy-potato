import pytest
from django.test import Client

from tests.factories import TodoFactory, UserFactory


@pytest.mark.django_db
def test_task_page_requires_authentication() -> None:
    response = Client().get("/tasks/")

    assert response.status_code == 302
    assert response["Location"] == "/accounts/login/?next=/tasks/"


@pytest.mark.django_db
def test_task_page_lists_only_the_authenticated_users_tasks() -> None:
    user = UserFactory.create()
    other_user = UserFactory.create()
    task = TodoFactory.create(
        user=user,
        title="Visible task",
        description="Task details",
        completed=True,
    )
    open_task = TodoFactory.create(user=user, title="Open task")
    TodoFactory.create(user=other_user, title="Private task")
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert task.title in response.content.decode()
    assert open_task.title in response.content.decode()
    assert "Task details" in response.content.decode()
    assert "Completed" in response.content.decode()
    assert "Open" in response.content.decode()
    assert "Private task" not in response.content.decode()


@pytest.mark.django_db
def test_task_page_shows_an_empty_state() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert "No tasks yet." in response.content.decode()
