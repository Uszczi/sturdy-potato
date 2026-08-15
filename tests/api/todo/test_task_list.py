from collections.abc import Callable

import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient

from tests.factories import TodoFactory, UserFactory


@freeze_time("2024-01-01T12:00:00Z", auto_tick_seconds=1)
@pytest.mark.django_db
def test_task_list_matches_snapshot(
    load_snapshot: Callable[[str], object],
) -> None:
    user = UserFactory.create()
    TodoFactory.create(
        id=1,
        user=user,
        title="Older task",
        description="Older details",
        completed=False,
    )
    TodoFactory.create(
        id=2,
        user=user,
        title="Newer task",
        description="Newer details",
        completed=True,
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/tasks/")

    assert response.status_code == 200
    assert response.json() == load_snapshot("task_list.json")
