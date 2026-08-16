from importlib import import_module

import pytest
from django.apps import apps

from infrastructure.models import Project, Todo
from tests.factories import ProjectFactory, TodoFactory, UserFactory

migration = import_module("infrastructure.migrations.0004_project_todo_position")


@pytest.mark.django_db
def test_backfill_positions_orders_projects_and_tasks_per_user() -> None:
    user = UserFactory.create()
    second_project = ProjectFactory.create(user=user, name="Beta", position=0)
    first_project = ProjectFactory.create(user=user, name="Alpha", position=0)
    older_task = TodoFactory.create(user=user, title="Older", position=0)
    newer_task = TodoFactory.create(user=user, title="Newer", position=0)

    migration.backfill_positions(apps, None)

    first_project.refresh_from_db()
    second_project.refresh_from_db()
    older_task.refresh_from_db()
    newer_task.refresh_from_db()

    # Projects are ordered by name, so "Alpha" comes before "Beta".
    assert first_project.position == 0
    assert second_project.position == 1
    # Tasks are ordered by "-created_at", so the newest task comes first.
    assert newer_task.position == 0
    assert older_task.position == 1


@pytest.mark.django_db
def test_backfill_positions_handles_an_empty_database() -> None:
    migration.backfill_positions(apps, None)

    assert not Project.objects.exists()
    assert not Todo.objects.exists()
