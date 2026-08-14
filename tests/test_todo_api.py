import pytest
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
