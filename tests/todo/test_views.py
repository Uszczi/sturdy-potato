import pytest
from django.test import Client

from infrastructure.models import Todo
from tests.factories import TodoFactory, UserFactory


@pytest.mark.django_db
def test_task_page_requires_authentication() -> None:
    response = Client().get("/tasks/")

    assert response.status_code == 403


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
def test_task_page_shows_an_empty_state() -> None:
    user = UserFactory.create()
    client = Client()
    client.force_login(user)

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert "No tasks yet." in response.content.decode()


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
