import pytest
from rest_framework.test import APIClient

from infrastructure.models import Project, Todo
from tests.factories import ProjectFactory, TodoFactory, UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_project_schema_describes_project_requests_and_responses(
    api_client: APIClient,
) -> None:
    response = api_client.get("/api/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    project_path = response.json()["paths"]["/api/projects/"]
    request_schema = project_path["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    response_schema = project_path["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"]
    task_request_schema = response.json()["paths"]["/api/tasks/"]["post"][
        "requestBody"
    ]["content"]["application/json"]["schema"]

    assert request_schema["title"] == "ProjectCreateInput"
    assert response_schema["title"] == "ProjectSchema"
    assert {"type": "integer"} in task_request_schema["properties"]["project_id"][
        "anyOf"
    ]


@pytest.mark.django_db
def test_project_list_requires_authentication(api_client: APIClient) -> None:
    response = api_client.get("/api/projects/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_list_returns_only_the_authenticated_users_projects(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Visible project")
    ProjectFactory.create(name="Private project")
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/projects/")

    assert response.status_code == 200
    assert response.json()[0]["id"] == project.id
    assert response.json()[0]["name"] == "Visible project"
    assert response.json()[0]["task_count"] == 0


@pytest.mark.django_db
def test_project_can_be_created_and_duplicate_names_are_rejected(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/projects/",
        {"name": "Roadmap"},
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Roadmap"
    assert Project.objects.filter(user=user, name="Roadmap").exists()

    duplicate_response = api_client.post(
        "/api/projects/",
        {"name": "Roadmap"},
        format="json",
    )

    assert duplicate_response.status_code == 400
    assert "name" in duplicate_response.json()["errors"]


@pytest.mark.django_db
def test_project_order_can_be_reordered_for_the_authenticated_user(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    first_project = ProjectFactory.create(user=user, name="First")
    second_project = ProjectFactory.create(user=user, name="Second")
    private_project = ProjectFactory.create(name="Private")
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/projects/reorder/",
        {"order": [second_project.id, first_project.id]},
        format="json",
    )

    assert response.status_code == 204
    assert [project["id"] for project in api_client.get("/api/projects/").json()] == [
        second_project.id,
        first_project.id,
    ]
    assert private_project.position == 0


@pytest.mark.django_db
def test_project_reorder_rejects_another_users_project(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user)
    private_project = ProjectFactory.create()
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/projects/reorder/",
        {"order": [project.id, private_project.id]},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_task_can_be_assigned_to_and_cleared_from_a_project(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    api_client.force_authenticate(user=user)

    create_response = api_client.post(
        "/api/tasks/",
        {"title": "Prepare launch", "project_id": project.id},
        format="json",
    )
    task_id = create_response.json()["id"]

    assert create_response.status_code == 201
    assert create_response.json()["project_id"] == project.id
    assert project.tasks.filter(id=task_id).exists()

    clear_response = api_client.patch(
        f"/api/tasks/{task_id}/",
        {"project_id": None},
        format="json",
    )

    assert clear_response.status_code == 200
    assert clear_response.json()["project_id"] is None
    assert Todo.objects.get(id=task_id).project_id is None


@pytest.mark.django_db
def test_task_cannot_be_assigned_to_another_users_project(
    api_client: APIClient,
) -> None:
    user = UserFactory.create()
    other_project = ProjectFactory.create(name="Private project")
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/tasks/",
        {"title": "Private assignment", "project_id": other_project.id},
        format="json",
    )

    assert response.status_code == 404
    assert not Todo.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_deleting_a_project_unassigns_its_tasks(api_client: APIClient) -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user)
    task = TodoFactory.create(user=user, project=project)
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/projects/{project.id}/")

    task.refresh_from_db()
    assert response.status_code == 204
    assert task.project_id is None
