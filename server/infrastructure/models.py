from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infrastructure_project"
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_project_name_per_user",
            ),
        ]
        # Every project query filters by user then orders by position; a
        # composite index serves that directly (a lone position index did not).
        indexes = [  # noqa: RUF012
            models.Index(fields=["user", "position"]),
        ]

    def __str__(self) -> str:
        return self.name


class Todo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todos",
    )
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "todo_todo"
        # Matches the repository access patterns: list-all (user, position)
        # and the open-tasks view (user, completed, position).
        indexes = [  # noqa: RUF012
            models.Index(fields=["user", "position"]),
            models.Index(fields=["user", "completed", "position"]),
        ]

    def __str__(self) -> str:
        return self.title
