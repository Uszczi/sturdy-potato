import getpass
import os
import sys
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

from infrastructure.models import Project, Todo, User

DEFAULT_SUPERUSER_USERNAME = "admin"
DEFAULT_SUPERUSER_EMAIL = "admin@example.com"
DEFAULT_DEMO_USERNAME = "demo"
DEFAULT_DEMO_EMAIL = "demo@example.com"

SEEDED_PROJECTS = (
    (
        "Getting started",
        (
            (
                "Explore the todo list",
                "Review the seeded tasks and mark one complete.",
                False,
            ),
            (
                "Create your first task",
                "Use the API or web interface to add a task.",
                False,
            ),
            (
                "Ship the next feature",
                "Turn the next idea into a small, working improvement.",
                True,
            ),
        ),
    ),
    (
        "Weekly planning",
        (
            (
                "Review weekly priorities",
                "Choose the work that deserves attention this week.",
                False,
            ),
            (
                "Block focus time",
                "Protect a quiet block for the most important task.",
                False,
            ),
            (
                "Tidy the inbox",
                "Give every loose task a useful next step.",
                False,
            ),
            (
                "Plan Friday wrap-up",
                "Leave a short note about what should happen next.",
                False,
            ),
        ),
    ),
    (
        "Product launch",
        (
            (
                "Confirm launch scope",
                "Make the smallest useful launch plan explicit.",
                False,
            ),
            (
                "Draft release notes",
                "Capture the changes people need to know about.",
                False,
            ),
            (
                "Prepare demo environment",
                "Make the happy path easy to show and verify.",
                False,
            ),
            (
                "Invite early testers",
                "Ask a small group for focused feedback.",
                False,
            ),
            (
                "Schedule launch review",
                "Set aside time to review the final readiness checklist.",
                False,
            ),
        ),
    ),
)


class Command(BaseCommand):
    help = "Seed the database with a superuser and demo project data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--superuser-username",
            default=DEFAULT_SUPERUSER_USERNAME,
            help=f"Username for the seeded superuser (default: {DEFAULT_SUPERUSER_USERNAME}).",
        )
        parser.add_argument(
            "--superuser-email",
            default=DEFAULT_SUPERUSER_EMAIL,
            help=f"Email for the seeded superuser (default: {DEFAULT_SUPERUSER_EMAIL}).",
        )
        parser.add_argument(
            "--superuser-password",
            help="Password for a newly created superuser. Prefer SEEDDB_SUPERUSER_PASSWORD.",
        )
        parser.add_argument(
            "--demo-username",
            default=DEFAULT_DEMO_USERNAME,
            help=f"Username for the seeded demo user (default: {DEFAULT_DEMO_USERNAME}).",
        )
        parser.add_argument(
            "--demo-email",
            default=DEFAULT_DEMO_EMAIL,
            help=f"Email for the seeded demo user (default: {DEFAULT_DEMO_EMAIL}).",
        )
        parser.add_argument(
            "--demo-password",
            help="Password for a newly created demo user. Prefer SEEDDB_DEMO_PASSWORD.",
        )
        parser.add_argument(
            "--skip-demo-data",
            action="store_true",
            help="Only seed the superuser, without a demo user or todos.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        with transaction.atomic():
            superuser, superuser_created = self._get_or_create_superuser(
                username=options["superuser_username"],
                email=options["superuser_email"],
                password=options["superuser_password"],
            )

            demo_user = None
            demo_user_created = False
            project_count = 0
            todo_count = 0
            if not options["skip_demo_data"]:
                if options["superuser_username"] == options["demo_username"]:
                    raise CommandError(
                        "The superuser and demo user must have different usernames."
                    )

                demo_user, demo_user_created = self._get_or_create_demo_user(
                    username=options["demo_username"],
                    email=options["demo_email"],
                    password=options["demo_password"],
                )
                project_count, todo_count = self._seed_projects_and_todos(demo_user)

        superuser_status = "Created" if superuser_created else "Found"
        self.stdout.write(f"{superuser_status} superuser '{superuser.username}'.")

        if demo_user is not None:
            demo_status = "Created" if demo_user_created else "Found"
            self.stdout.write(f"{demo_status} demo user '{demo_user.username}'.")
            self.stdout.write(f"Created {project_count} new demo project(s).")
            self.stdout.write(f"Created {todo_count} new demo todo(s).")

    def _get_or_create_superuser(
        self,
        username: str,
        email: str,
        password: str | None,
    ) -> tuple[User, bool]:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(
                self._resolve_password(
                    password,
                    "SEEDDB_SUPERUSER_PASSWORD",
                    "--superuser-password",
                    username,
                )
            )
            user.save(update_fields=["password"])
            return user, True

        if not user.is_superuser:
            raise CommandError(
                f"User '{username}' already exists but is not a superuser."
            )

        updates: list[str] = []
        if not user.is_active:
            user.is_active = True
            updates.append("is_active")
        if not user.is_staff:
            user.is_staff = True
            updates.append("is_staff")
        if updates:
            user.save(update_fields=updates)
        return user, False

    def _get_or_create_demo_user(
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
            user.set_password(
                self._resolve_password(
                    password,
                    "SEEDDB_DEMO_PASSWORD",
                    "--demo-password",
                    username,
                )
            )
            user.save(update_fields=["password"])
        return user, created

    def _seed_projects_and_todos(self, user: User) -> tuple[int, int]:
        project_count = 0
        todo_count = 0
        for project_position, (project_name, todos) in enumerate(SEEDED_PROJECTS):
            project, project_created = Project.objects.get_or_create(
                user=user,
                name=project_name,
                defaults={"position": project_position},
            )
            project_count += int(project_created)
            for task_position, (title, description, completed) in enumerate(todos):
                _, todo_created = Todo.objects.get_or_create(
                    user=user,
                    project=project,
                    title=title,
                    defaults={
                        "description": description,
                        "completed": completed,
                        "position": task_position,
                    },
                )
                todo_count += int(todo_created)
        return project_count, todo_count

    def _resolve_password(
        self,
        supplied_password: str | None,
        environment_name: str,
        option_name: str,
        username: str,
    ) -> str:
        password = supplied_password
        if password is None:
            password = os.environ.get(environment_name)
        if password is None and sys.stdin.isatty():
            password = getpass.getpass(f"Password for {username}: ")
        if not password:
            raise CommandError(
                f"Provide {option_name} or {environment_name} when creating '{username}'."
            )
        return password
