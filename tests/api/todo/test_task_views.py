import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from tests.factories import ProjectFactory, TodoFactory, UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_view_defaults_to_inbox_and_returns_only_unassigned_tasks() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user)
    inbox_task = TodoFactory.create(user=user, title="Inbox task")
    TodoFactory.create(user=user, title="Project task", project=project)
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/view/")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [inbox_task.id]


@pytest.mark.django_db
def test_view_filters_by_project() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user)
    project_task = TodoFactory.create(user=user, title="Project task", project=project)
    TodoFactory.create(user=user, title="Inbox task")
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/tasks/view/?project={project.id}")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [project_task.id]


@pytest.mark.django_db
def test_view_returns_404_for_a_project_owned_by_another_user() -> None:
    user = UserFactory.create()
    other_project = ProjectFactory.create()
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/tasks/view/?project={other_project.id}")

    assert response.status_code == 404


@freeze_time("2024-01-01T12:00:00Z")
@pytest.mark.django_db
def test_view_today_returns_tasks_due_today() -> None:
    user = UserFactory.create()
    due_today = TodoFactory.create(user=user, title="Due today", due_date="2024-01-01")
    TodoFactory.create(user=user, title="Due later", due_date="2024-01-02")
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/view/?view=today")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [due_today.id]


@freeze_time("2024-01-01T12:00:00Z")
@pytest.mark.django_db
def test_view_upcoming_returns_open_tasks_due_after_today() -> None:
    user = UserFactory.create()
    upcoming = TodoFactory.create(user=user, title="Upcoming", due_date="2024-01-02")
    TodoFactory.create(user=user, title="Due today", due_date="2024-01-01")
    TodoFactory.create(
        user=user,
        title="Completed upcoming",
        due_date="2024-01-03",
        completed=True,
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/view/?view=upcoming")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [upcoming.id]


@pytest.mark.django_db
def test_open_returns_only_incomplete_tasks() -> None:
    user = UserFactory.create()
    open_task = TodoFactory.create(user=user, title="Open task")
    TodoFactory.create(user=user, title="Done task", completed=True)
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/open/")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [open_task.id]


@pytest.mark.django_db
def test_open_respects_the_limit_query_param() -> None:
    user = UserFactory.create()
    TodoFactory.create(user=user, title="First", position=0)
    TodoFactory.create(user=user, title="Second", position=1)
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/open/?limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_count_returns_the_total_number_of_tasks() -> None:
    user = UserFactory.create()
    TodoFactory.create(user=user, completed=False)
    TodoFactory.create(user=user, completed=True)
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/count/")

    assert response.status_code == 200
    assert response.json() == {"count": 2}


@pytest.mark.django_db
def test_count_can_filter_by_completion() -> None:
    user = UserFactory.create()
    TodoFactory.create(user=user, completed=False)
    TodoFactory.create(user=user, completed=True)
    TodoFactory.create(user=user, completed=True)
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    assert api_client.get("/api/tasks/count/?completed=true").json() == {"count": 2}
    assert api_client.get("/api/tasks/count/?completed=false").json() == {"count": 1}
