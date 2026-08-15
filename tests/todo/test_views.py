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
    assert "Mark as open" in response.content.decode()
    assert "Mark as complete" in response.content.decode()
    assert "Private task" not in response.content.decode()


@pytest.mark.django_db
def test_task_page_shows_an_empty_state() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert "No tasks yet." in response.content.decode()


@pytest.mark.django_db
def test_task_toggle_updates_completion_and_returns_the_task_partial() -> None:
    user = UserFactory.create()
    task = TodoFactory.create(user=user, completed=False)
    client = Client()
    client.force_login(user)

    response = client.post(f"/tasks/{task.id}/toggle/", HTTP_HX_REQUEST="true")

    task.refresh_from_db()
    assert response.status_code == 200
    assert task.completed is True
    assert response.templates[0].name == "todo/_task.html"
    assert "Completed" in response.content.decode()
    assert "Mark as open" in response.content.decode()

    response = client.post(f"/tasks/{task.id}/toggle/", HTTP_HX_REQUEST="true")

    task.refresh_from_db()
    assert response.status_code == 200
    assert task.completed is False
    assert "Open" in response.content.decode()
    assert "Mark as complete" in response.content.decode()


@pytest.mark.django_db
def test_task_toggle_does_not_change_another_users_task() -> None:
    owner = UserFactory.create()
    other_user = UserFactory.create()
    task = TodoFactory.create(user=owner, completed=False)
    client = Client()
    client.force_login(other_user)

    response = client.post(f"/tasks/{task.id}/toggle/", HTTP_HX_REQUEST="true")

    task.refresh_from_db()
    assert response.status_code == 404
    assert task.completed is False


@pytest.mark.django_db
def test_task_toggle_requires_authentication() -> None:
    task = TodoFactory.create(completed=False)

    response = Client().post(f"/tasks/{task.id}/toggle/", HTTP_HX_REQUEST="true")

    assert response.status_code == 302
    assert response["Location"] == (
        f"/accounts/login/?next=/tasks/{task.id}/toggle/"
    )
