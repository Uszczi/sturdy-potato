import os
import sys
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

from infrastructure.models import Project, Todo, User

DEFAULT_HEAVY_USERNAME = "heavy"
DEFAULT_HEAVY_EMAIL = "heavy@example.com"
DEFAULT_PROJECTS = 100
DEFAULT_TASKS_PER_PROJECT = 1000
BULK_BATCH_SIZE = 1000


class Command(BaseCommand):
    help = (
        "Seed a heavy demo user with a large number of projects and tasks. "
        "Defaults to 100 projects with 1000 tasks each."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--username",
            default=DEFAULT_HEAVY_USERNAME,
            help=f"Username for the heavy demo user (default: {DEFAULT_HEAVY_USERNAME}).",
        )
        parser.add_argument(
            "--email",
            default=DEFAULT_HEAVY_EMAIL,
            help=f"Email for the heavy demo user (default: {DEFAULT_HEAVY_EMAIL}).",
        )
        parser.add_argument(
            "--password",
            help="Password for a newly created user. Prefer SEEDDB_HEAVY_PASSWORD.",
        )
        parser.add_argument(
            "--projects",
            type=int,
            default=DEFAULT_PROJECTS,
            help=f"Number of projects to create (default: {DEFAULT_PROJECTS}).",
        )
        parser.add_argument(
            "--tasks-per-project",
            type=int,
            default=DEFAULT_TASKS_PER_PROJECT,
            help=(
                "Number of tasks to create per project "
                f"(default: {DEFAULT_TASKS_PER_PROJECT})."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        projects = options["projects"]
        tasks_per_project = options["tasks_per_project"]
        if projects < 0 or tasks_per_project < 0:
            raise CommandError("--projects and --tasks-per-project must be non-negative.")

        with transaction.atomic():
            user, user_created = self._get_or_create_user(
                username=options["username"],
                email=options["email"],
                password=options["password"],
            )
            project_count, todo_count = self._seed(user, projects, tasks_per_project)

        user_status = "Created" if user_created else "Found"
        self.stdout.write(f"{user_status} heavy demo user '{user.username}'.")
        self.stdout.write(f"Created {project_count} new project(s).")
        self.stdout.write(f"Created {todo_count} new task(s).")

    def _get_or_create_user(
        self,
        username: str,
        email: str,
        password: str | None,
    ) -> tuple[User, bool]:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )
        if created:
            user.set_password(self._resolve_password(password, username))
            user.save(update_fields=["password"])
        return user, created

    def _seed(
        self,
        user: User,
        projects: int,
        tasks_per_project: int,
    ) -> tuple[int, int]:
        existing_names = set(
            Project.objects.filter(user=user).values_list("name", flat=True)
        )
        base_position = (
            Project.objects.filter(user=user).count()
        )

        new_projects = []
        position = base_position
        for index in range(projects):
            name = f"Heavy project {index + 1:03d}"
            if name in existing_names:
                continue
            new_projects.append(
                Project(user=user, name=name, position=position)
            )
            position += 1

        Project.objects.bulk_create(new_projects, batch_size=BULK_BATCH_SIZE)

        todos = []
        for project in new_projects:
            for task_index in range(tasks_per_project):
                todos.append(
                    Todo(
                        user=user,
                        project=project,
                        title=f"{project.name} task {task_index + 1:04d}",
                        description=(
                            f"Auto-generated task {task_index + 1} "
                            f"for {project.name}."
                        ),
                        completed=(task_index % 3 == 0),
                        position=task_index,
                    )
                )

        Todo.objects.bulk_create(todos, batch_size=BULK_BATCH_SIZE)
        return len(new_projects), len(todos)

    def _resolve_password(self, supplied_password: str | None, username: str) -> str:
        password = supplied_password or os.environ.get("SEEDDB_HEAVY_PASSWORD")
        if password is None and sys.stdin.isatty():
            import getpass

            password = getpass.getpass(f"Password for {username}: ")
        if not password:
            raise CommandError(
                "Provide --password or SEEDDB_HEAVY_PASSWORD when creating "
                f"'{username}'."
            )
        return password
