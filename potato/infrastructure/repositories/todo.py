from django.db.models import QuerySet
from potato.models import User

from infrastructure.models import Todo


class TodoRepository:
    def list_for_user(self, user: User) -> QuerySet[Todo]:
        return Todo.objects.filter(user=user).order_by("-created_at")
