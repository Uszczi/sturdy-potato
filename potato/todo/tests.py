from django.contrib.auth import get_user_model
from django.test import TestCase
from infrastructure.models import Todo
from rest_framework.test import APIClient


class TaskListApiTests(TestCase):
    def setUp(self) -> None:
        self.api_client = APIClient()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="owner",
            password="password",
        )
        self.other_user = user_model.objects.create_user(
            username="other",
            password="password",
        )

    def test_requires_authentication(self) -> None:
        response = self.api_client.get("/api/tasks/")

        self.assertEqual(response.status_code, 403)

    def test_lists_only_the_authenticated_users_tasks(self) -> None:
        first_task = Todo.objects.create(user=self.user, title="First task")
        second_task = Todo.objects.create(user=self.user, title="Second task")
        Todo.objects.create(user=self.other_user, title="Private task")
        self.api_client.force_authenticate(user=self.user)

        response = self.api_client.get("/api/tasks/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [task["id"] for task in response.json()],
            [second_task.id, first_task.id],
        )
