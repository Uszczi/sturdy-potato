from datetime import timedelta

import pytest
from asgiref.sync import async_to_sync
from django.test import Client
from django.utils import timezone
from rest_framework.exceptions import NotFound

from infrastructure.models import Project, Todo
from infrastructure.repositories import TodoRepository
from tests.factories import ProjectFactory, TodoFactory, UserFactory
from web.views import _resolve_task_project


@pytest.mark.django_db
def test_home_page_redirects_anonymous_users_to_the_login_page() -> None:
    response = Client().get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/accounts/login/?next=/"


@pytest.mark.django_db
def test_task_page_requires_authentication() -> None:
    response = Client().get("/tasks/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_home_page_shows_the_workspace_overview_and_responsive_navigation() -> None:
    user = UserFactory.create(username="planner")
    project = ProjectFactory.create(user=user, name="Launch")
    TodoFactory.create(user=user, project=project, title="Prepare launch")
    TodoFactory.create(user=user, completed=True, title="Finished task")
    client = Client()
    client.force_login(user)

    response = client.get("/")

    content = response.content.decode()
    assert response.status_code == 200
    assert "Prepare launch" in content
    assert "Launch" in content
    assert "Today" in content
    assert "Upcoming" in content
    assert "lg:translate-x-0" in content
    assert "Open navigation" in content
    assert "planner" in content


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
    assert "alpinejs@3.x.x" in response.content.decode()
    assert "Open navigation" in response.content.decode()
    assert "modal-open" in response.content.decode()
    assert "container mx-auto" in response.content.decode()
    assert "divide-y divide-base-300" in response.content.decode()
    assert "card card-border" not in response.content.decode()
    assert "btn-circle" in response.content.decode()
    assert 'aria-label="Mark Visible task as open"' in response.content.decode()
    assert 'aria-label="Mark Open task as complete"' in response.content.decode()
    assert "Click for details" not in response.content.decode()
    assert 'name="title"' in response.content.decode()
    assert "Add task" in response.content.decode()
    assert 'data-title="Visible task"' in response.content.decode()
    assert 'data-description="Task details"' in response.content.decode()
    assert response.content.decode().index(
        "Open task"
    ) < response.content.decode().index("Visible task")
    assert "Private task" not in response.content.decode()


@pytest.mark.django_db
def test_inbox_page_only_lists_tasks_without_a_project() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    inbox_task = TodoFactory.create(user=user, title="Unassigned task")
    TodoFactory.create(user=user, project=project, title="Project task")
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/")

    content = response.content.decode()
    assert response.status_code == 200
    assert inbox_task.title in content
    assert "Project task" not in content


@pytest.mark.django_db
def test_task_page_shows_an_empty_state() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert "No tasks yet." in response.content.decode()


@pytest.mark.django_db
def test_task_page_can_open_the_quick_add_composer() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/?compose=1")

    content = response.content.decode()
    assert response.status_code == 200
    assert "composerOpen: true" in content
    assert "What needs to be done?" in content


@pytest.mark.django_db
def test_task_page_filters_today_and_upcoming_views_by_due_date() -> None:
    user = UserFactory.create()
    today = timezone.localdate()
    TodoFactory.create(user=user, title="Due today", due_date=today)
    TodoFactory.create(
        user=user,
        title="Due tomorrow",
        due_date=today + timedelta(days=1),
    )
    TodoFactory.create(
        user=user,
        title="Completed later",
        due_date=today + timedelta(days=2),
        completed=True,
    )
    client = Client()
    client.force_login(user)

    today_response = client.get("/tasks/?view=today")
    upcoming_response = client.get("/tasks/?view=upcoming")

    today_content = today_response.content.decode()
    upcoming_content = upcoming_response.content.decode()
    assert "Today" in today_content
    assert "Due today" in today_content
    assert "Due tomorrow" not in today_content
    assert "Upcoming" in upcoming_content
    assert "Due tomorrow" in upcoming_content
    assert "Completed later" not in upcoming_content


@pytest.mark.django_db
def test_projects_page_lists_only_the_authenticated_users_projects() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Visible project")
    ProjectFactory.create(name="Private project")
    client = Client()
    client.force_login(user)

    response = client.get("/projects/")

    assert response.status_code == 200
    assert "Projects" in response.content.decode()
    assert project.name in response.content.decode()
    assert "Private project" not in response.content.decode()
    assert "0 tasks" in response.content.decode()
    assert "Open navigation" in response.content.decode()


@pytest.mark.django_db
def test_project_page_lists_only_the_authenticated_users_tasks_for_that_project() -> (
    None
):
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    other_project = ProjectFactory.create(user=user, name="Maintenance")
    TodoFactory.create(user=user, project=project, title="Prepare launch")
    TodoFactory.create(user=user, project=other_project, title="Update dependencies")
    private_project = ProjectFactory.create(name="Private project")
    TodoFactory.create(
        user=private_project.user,
        project=private_project,
        title="Private task",
    )
    client = Client()
    client.force_login(user)

    response = client.get(f"/projects/{project.id}/")

    content = response.content.decode()
    assert response.status_code == 200
    assert "Launch" in content
    assert "Prepare launch" in content
    assert "Update dependencies" not in content
    assert "Private task" not in content
    assert f'hx-post="/tasks/create/?project={project.id}"' in content
    assert 'aria-label="Mark Prepare launch as complete"' in content


@pytest.mark.django_db
def test_project_page_requires_an_owned_project() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get(f"/projects/{project.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_projects_page_can_add_a_project() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.post(
        "/projects/create/",
        {"name": "New project"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert response.templates[0].name == "projects/_project_section.html"
    project = Project.objects.get(user=user, name="New project")
    assert project.user_id == user.id
    assert "New project" in response.content.decode()


@pytest.mark.django_db
def test_task_page_can_add_a_task_and_replace_the_empty_state() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.post(
        "/tasks/create/",
        {"title": "New task"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert response.templates[0].name == "todo/_task_section.html"
    assert Todo.objects.filter(user=user, title="New task").exists()
    assert '<ul id="task-list"' in response.content.decode()
    assert "New task" in response.content.decode()
    assert "No tasks yet." not in response.content.decode()


@pytest.mark.django_db
def test_project_page_task_creation_keeps_the_new_task_in_that_project() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    client = Client()
    client.force_login(user)

    response = client.post(
        f"/tasks/create/?project={project.id}",
        {"title": "Prepare launch", "project_id": str(project.id)},
        HTTP_HX_REQUEST="true",
    )

    task = Todo.objects.get(user=user, title="Prepare launch")
    assert response.status_code == 200
    assert task.project_id == project.id
    assert "Prepare launch" in response.content.decode()


@pytest.mark.django_db
def test_task_creation_can_assign_a_project() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    due_date = timezone.localdate() + timedelta(days=1)
    client = Client()
    client.force_login(user)

    response = client.post(
        "/tasks/create/",
        {
            "title": "Prepare launch",
            "project_id": str(project.id),
            "due_date": due_date.isoformat(),
        },
        HTTP_HX_REQUEST="true",
    )

    task = Todo.objects.get(user=user, title="Prepare launch")
    assert response.status_code == 200
    assert task.project_id == project.id
    assert task.due_date == due_date
    assert "Prepare launch" not in response.content.decode()


@pytest.mark.django_db
def test_task_can_be_assigned_to_and_cleared_from_a_project() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    task = TodoFactory.create(user=user)
    client = Client()
    client.force_login(user)

    response = client.post(
        f"/tasks/{task.id}/project/",
        {"project_id": str(project.id)},
        HTTP_HX_REQUEST="true",
    )

    task.refresh_from_db()
    assert response.status_code == 200
    assert task.project_id == project.id
    assert response.templates[0].name == "todo/_task_section.html"

    client.post(
        f"/tasks/{task.id}/project/",
        {"project_id": ""},
        HTTP_HX_REQUEST="true",
    )

    task.refresh_from_db()
    assert task.project_id is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "title",
    (
        "",
        "x" * 201,
    ),
)
def test_task_create_validates_the_title(title: str) -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.post("/tasks/create/", {"title": title})

    assert response.status_code == 400
    assert "title" in response.json()["errors"]
    assert not Todo.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_task_create_rejects_non_mapping_input() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.post(
        "/tasks/create/",
        data="[]",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Expected a JSON object."


@pytest.mark.django_db
def test_task_create_requires_authentication() -> None:
    response = Client().post("/tasks/create/", {"title": "New task"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_task_toggle_updates_completion_and_returns_the_task_partial() -> None:
    user = UserFactory.create()
    task = TodoFactory.create(user=user, title="Move me", completed=False)
    open_task = TodoFactory.create(user=user, title="Keep open", completed=False)
    client = Client()
    client.force_login(user)

    response = client.post(f"/tasks/{task.id}/toggle/", HTTP_HX_REQUEST="true")

    task.refresh_from_db()
    assert response.status_code == 200
    assert task.completed is True
    assert response.templates[0].name == "todo/_task_list.html"
    assert 'aria-pressed="true"' in response.content.decode()
    assert f'aria-label="Mark {task.title} as open"' in response.content.decode()
    assert response.content.decode().index(
        open_task.title
    ) < response.content.decode().index(task.title)

    response = client.post(f"/tasks/{task.id}/toggle/", HTTP_HX_REQUEST="true")

    task.refresh_from_db()
    assert response.status_code == 200
    assert task.completed is False
    assert 'aria-pressed="false"' in response.content.decode()
    assert f'aria-label="Mark {task.title} as complete"' in response.content.decode()


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

    assert response.status_code == 403


@pytest.mark.django_db
def test_task_scope_rejects_a_non_numeric_project_query() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/?project=not-a-number")

    assert response.status_code == 404


@pytest.mark.django_db
def test_task_cannot_be_assigned_to_another_users_project() -> None:
    user = UserFactory.create()
    task = TodoFactory.create(user=user)
    other_project = ProjectFactory.create(name="Private project")
    client = Client()
    client.force_login(user)

    response = client.post(
        f"/tasks/{task.id}/project/",
        {"project_id": str(other_project.id)},
        HTTP_HX_REQUEST="true",
    )

    task.refresh_from_db()
    assert response.status_code == 404
    assert task.project_id is None


@pytest.mark.django_db
def test_projects_page_rejects_a_duplicate_project_name() -> None:
    user = UserFactory.create()
    ProjectFactory.create(user=user, name="Launch")
    client = Client()
    client.force_login(user)

    response = client.post(
        "/projects/create/",
        {"name": "Launch"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 400
    assert "name" in response.json()["errors"]
    assert Project.objects.filter(user=user, name="Launch").count() == 1


@pytest.mark.django_db
def test_resolve_task_project_returns_data_without_a_project_id() -> None:
    user = UserFactory.create()

    data = async_to_sync(_resolve_task_project)(
        TodoRepository(), user, {"title": "Keep me"}
    )

    assert data == {"title": "Keep me"}


@pytest.mark.django_db
def test_resolve_task_project_rejects_a_non_integer_project_id() -> None:
    user = UserFactory.create()

    with pytest.raises(NotFound):
        async_to_sync(_resolve_task_project)(
            TodoRepository(), user, {"project_id": "not-a-number"}
        )
