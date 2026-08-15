from collections.abc import Callable

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from tests.factories import TodoFactory, UserFactory


@freeze_time("2024-01-02T12:00:00Z")
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
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/tasks/{task.id}/")

    assert response.status_code == 200
    assert response.json() == load_snapshot("task_detail.json")
