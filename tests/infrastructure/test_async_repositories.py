import pytest
from asgiref.sync import async_to_sync

from infrastructure.async_repositories import (
    AsyncProjectRepository,
    AsyncTodoRepository,
)
from infrastructure.models import Project, Todo
from infrastructure.repositories import ProjectRepository, TodoRepository
from tests.factories import ProjectFactory, TodoFactory, UserFactory


@pytest.mark.django_db
def test_async_todo_repository_wraps_the_sync_repository() -> None:
    user = UserFactory.create()
    project = ProjectFactory.create(user=user, name="Launch")
    repo = AsyncTodoRepository(TodoRepository())

    created = async_to_sync(repo.create_for_user)(user, {"title": "Write tests"})
    assert created.title == "Write tests"

    listed = async_to_sync(repo.list_for_user)(user)
    assert [task.title for task in listed] == ["Write tests"]

    fetched = async_to_sync(repo.get_for_user)(user, created.id)
    assert fetched is not None and fetched.id == created.id

    fetched_project = async_to_sync(repo.get_project_for_user)(user, project.id)
    assert fetched_project is not None and fetched_project.id == project.id

    updated = async_to_sync(repo.update)(created, {"completed": True})
    assert updated.completed is True

    second = async_to_sync(repo.create_for_user)(user, {"title": "Second"})
    assert async_to_sync(repo.reorder_for_user)(user, [second.id, created.id]) is True

    async_to_sync(repo.delete)(created)
    assert not Todo.objects.filter(id=created.id).exists()


@pytest.mark.django_db
def test_async_project_repository_wraps_the_sync_repository() -> None:
    user = UserFactory.create()
    repo = AsyncProjectRepository(ProjectRepository())

    created = async_to_sync(repo.create_for_user)(user, {"name": "Launch"})
    assert created.name == "Launch"

    listed = async_to_sync(repo.list_for_user)(user)
    assert [project.name for project in listed] == ["Launch"]

    fetched = async_to_sync(repo.get_for_user)(user, created.id)
    assert fetched is not None and fetched.id == created.id

    updated = async_to_sync(repo.update)(created, {"name": "Relaunch"})
    assert updated.name == "Relaunch"

    second = async_to_sync(repo.create_for_user)(user, {"name": "Second"})
    assert async_to_sync(repo.reorder_for_user)(user, [second.id, created.id]) is True

    async_to_sync(repo.delete)(created)
    assert not Project.objects.filter(id=created.id).exists()


@pytest.mark.django_db
def test_async_todo_repository_returns_none_for_missing_records() -> None:
    user = UserFactory.create()
    other_task = TodoFactory.create()
    repo = AsyncTodoRepository(TodoRepository())

    assert async_to_sync(repo.get_for_user)(user, other_task.id) is None
    assert async_to_sync(repo.get_project_for_user)(user, 999) is None
