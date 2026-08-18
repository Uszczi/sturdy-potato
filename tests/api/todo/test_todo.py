import pytest
from rest_framework.test import APIClient

from infrastructure.models import Todo, User
from tests.factories import TodoFactory, UserFactory


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
def test_api_root_lists_the_task_resource(api_client: APIClient) -> None:
    response = api_client.get("/api/")

    assert response.status_code == 200
    assert response.json()["tasks"].endswith("/api/tasks/")
    assert response.json()["projects"].endswith("/api/projects/")


@pytest.mark.django_db
def test_task_create_schema_describes_the_pydantic_request_model(
    api_client: APIClient,
) -> None:
    response = api_client.get("/api/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    request_schema = response.json()["paths"]["/api/tasks/"]["post"]["requestBody"][
        "content"
    ]["application/json"]["schema"]
    assert request_schema["title"] == "TodoCreateInput"
    assert request_schema["properties"]["title"]["maxLength"] == 200
    assert request_schema["properties"]["title"]["minLength"] == 1

    update_schema = response.json()["paths"]["/api/tasks/{id}/"]["patch"][
        "requestBody"
    ]["content"]["application/json"]["schema"]
    assert update_schema["title"] == "TodoUpdateInput"

    list_response_schema = response.json()["paths"]["/api/tasks/"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]["schema"]
    assert list_response_schema["type"] == "array"
    assert list_response_schema["items"]["title"] == "TodoSchema"

    create_response_schema = response.json()["paths"]["/api/tasks/"]["post"][
        "responses"
    ]["201"]["content"]["application/json"]["schema"]
    assert create_response_schema["title"] == "TodoSchema"


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
def test_task_order_can_be_reordered_for_the_authenticated_user(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    first_task = TodoFactory.create(user=user, title="First task")
    second_task = TodoFactory.create(user=user, title="Second task")
    private_task = TodoFactory.create(title="Private task")
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/reorder/",
        {"order": [first_task.id, second_task.id]},
        format="json",
    )

    assert response.status_code == 204
    assert [task["id"] for task in api_client.get("/api/tasks/").json()] == [
        first_task.id,
        second_task.id,
    ]
    assert private_task.position == 0


@pytest.mark.django_db
def test_task_reorder_rejects_another_users_task(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    task = TodoFactory.create(user=user)
    private_task = TodoFactory.create()
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/reorder/",
        {"order": [task.id, private_task.id]},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_task_detail_requires_authentication(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    task = TodoFactory.create(user=users[0])

    response = api_client.get(f"/api/tasks/{task.id}/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_task_detail_returns_the_same_task_shape_as_the_list(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, other_user = users
    task = TodoFactory.create(
        user=user,
        title="Task details",
        description="Details",
        completed=True,
    )
    other_task = TodoFactory.create(user=other_user, title="Private task")
    api_client.force_authenticate(user=user)

    detail_response = api_client.get(f"/api/tasks/{task.id}/")
    list_response = api_client.get("/api/tasks/")
    other_response = api_client.get(f"/api/tasks/{other_task.id}/")

    assert detail_response.status_code == 200
    assert isinstance(detail_response.json(), dict)
    assert detail_response.json() in list_response.json()
    assert detail_response.json()["description"] == "Details"
    assert detail_response.json()["completed"] is True
    assert other_response.status_code == 404


@pytest.mark.django_db
def test_task_can_be_created(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/",
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
def test_task_creation_uses_defaults_and_validates_title(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert "title" in response.json()["errors"]

    response = api_client.post(
        "/api/tasks/",
        {"title": "x" * 201},
        format="json",
    )

    assert response.status_code == 400
    assert "title" in response.json()["errors"]

    response = api_client.post(
        "/api/tasks/",
        {"title": "Task with defaults"},
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["description"] == ""
    assert response.json()["completed"] is False


@pytest.mark.django_db
def test_task_creation_requires_a_json_object(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/",
        [],
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Expected a JSON object."


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
        f"/api/tasks/{task.id}/",
        {"title": "Updated task", "completed": True},
        format="json",
    )
    other_response = api_client.patch(
        f"/api/tasks/{other_task.id}/",
        {"title": "Should remain private"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["completed"] is True
    assert other_response.status_code == 404


@pytest.mark.django_db
def test_task_can_be_partially_updated(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    task = TodoFactory.create(
        user=user,
        title="Original task",
        description="Keep this description",
        completed=False,
    )
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        f"/api/tasks/{task.id}/",
        {"title": "Updated task"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["description"] == "Keep this description"
    assert response.json()["completed"] is False


@pytest.mark.django_db
def test_task_update_requires_a_json_object(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    task = TodoFactory.create(user=users[0])
    api_client.force_authenticate(user=users[0])

    response = api_client.patch(
        f"/api/tasks/{task.id}/",
        [],
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Expected a JSON object."


@pytest.mark.django_db
def test_task_can_be_deleted(
    api_client: APIClient,
    users: tuple[User, User],
) -> None:
    user, _ = users
    task = TodoFactory.create(user=user)
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/tasks/{task.id}/")

    assert response.status_code == 204
    assert not Todo.objects.filter(id=task.id).exists()
