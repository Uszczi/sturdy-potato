import pytest
from infrastructure.models import Todo
from potato.models import User
from rest_framework.test import APIClient

from .factories import TodoFactory, UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def users() -> tuple[User, User]:
    return (
        UserFactory.create(),
        UserFactory.create(),
    )


@pytest.mark.django_db
def test_task_list_requires_authentication(api_client: APIClient) -> None:
    response = api_client.get("/api/tasks/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_task_list_returns_only_the_authenticated_users_tasks(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, other_user = users
    first_task = TodoFactory.create(user=user, title="First task")
    second_task = TodoFactory.create(user=user, title="Second task")
    TodoFactory.create(user=other_user, title="Private task")
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [
        second_task.id,
        first_task.id,
    ]


@pytest.mark.django_db
def test_task_can_be_created(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/create/",
        {
            "title": "New task",
            "description": "Task details",
            "completed": False,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["title"] == "New task"
    assert Todo.objects.filter(user=user, title="New task").exists()


@pytest.mark.django_db
def test_task_can_be_updated(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, other_user = users
    task = TodoFactory.create(user=user, title="Original task")
    other_task = TodoFactory.create(user=other_user, title="Private task")
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        f"/api/tasks/{task.id}/update/",
        {"title": "Updated task", "completed": True},
        format="json",
    )
    other_response = api_client.patch(
        f"/api/tasks/{other_task.id}/update/",
        {"title": "Should remain private"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["completed"] is True
    assert other_response.status_code == 404


@pytest.mark.django_db
def test_task_can_be_deleted(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    task = TodoFactory.create(user=user)
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/tasks/{task.id}/delete/")

    assert response.status_code == 204
    assert not Todo.objects.filter(id=task.id).exists()
