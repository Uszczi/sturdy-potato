from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from infrastructure.models import Todo
from rest_framework.test import APIClient

from tests.factories import TodoFactory, UserFactory


@pytest.mark.django_db
def test_task_list_matches_snapshot(
    load_snapshot: Callable[[str], object],
) -> None:
    user = UserFactory.create()
    older_task = TodoFactory.create(
        id=1,
        user=user,
        title="Older task",
        description="Older details",
        completed=False,
    )
    newer_task = TodoFactory.create(
        id=2,
        user=user,
        title="Newer task",
        description="Newer details",
        completed=True,
    )
    Todo.objects.filter(id=older_task.id).update(
        created_at=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
    )
    Todo.objects.filter(id=newer_task.id).update(
        created_at=datetime(2024, 1, 2, 12, 0, tzinfo=UTC),
        updated_at=datetime(2024, 1, 2, 12, 0, tzinfo=UTC),
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/")

    assert response.status_code == 200
    assert response.json() == load_snapshot("task_list.json")
