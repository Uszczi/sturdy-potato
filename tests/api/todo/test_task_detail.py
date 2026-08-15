from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from infrastructure.models import Todo
from rest_framework.test import APIClient

from tests.factories import TodoFactory, UserFactory


@pytest.mark.django_db
def test_task_detail_matches_snapshot(
    load_snapshot: Callable[[str], object],
) -> None:
    user = UserFactory.create()
    task = TodoFactory.create(
        id=1,
        user=user,
        title="Task details",
        description="Details for this task",
        completed=True,
    )
    Todo.objects.filter(id=task.id).update(
        created_at=datetime(2024, 1, 2, 12, 0, tzinfo=UTC),
        updated_at=datetime(2024, 1, 3, 12, 0, tzinfo=UTC),
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/tasks/{task.id}/")

    assert response.status_code == 200
    assert response.json() == load_snapshot("task_detail.json")
