import getpass
import sys
from io import StringIO
from unittest.mock import Mock

import pytest
from django.core.management import CommandError, call_command

from infrastructure.models import Project, Todo, User


@pytest.mark.django_db
def test_seedheavy_creates_a_user_with_projects_and_tasks() -> None:
    output = StringIO()

    call_command(
        "seedheavy",
        projects=2,
        tasks_per_project=4,
        password="heavy-password",
        stdout=output,
    )

    user = User.objects.get(username="heavy")
    assert user.email == "heavy@example.com"
    assert user.check_password("heavy-password")
    assert Project.objects.filter(user=user).count() == 2
    assert Todo.objects.filter(user=user).count() == 8
    # Every third task (0-indexed) is marked completed.
    assert Todo.objects.filter(user=user, completed=True).count() == 4
    assert "Created heavy demo user 'heavy'." in output.getvalue()
    assert "Created 2 new project(s)." in output.getvalue()
    assert "Created 8 new task(s)." in output.getvalue()


@pytest.mark.django_db
def test_seedheavy_is_idempotent_for_existing_projects() -> None:
    call_command("seedheavy", projects=2, tasks_per_project=1, password="secret")

    output = StringIO()
    call_command(
        "seedheavy",
        projects=2,
        tasks_per_project=1,
        password="ignored",
        stdout=output,
    )

    user = User.objects.get(username="heavy")
    assert Project.objects.filter(user=user).count() == 2
    assert Todo.objects.filter(user=user).count() == 2
    assert user.check_password("secret")
    assert "Found heavy demo user 'heavy'." in output.getvalue()
    assert "Created 0 new project(s)." in output.getvalue()
    assert "Created 0 new task(s)." in output.getvalue()


@pytest.mark.django_db
def test_seedheavy_rejects_negative_counts() -> None:
    with pytest.raises(CommandError, match="must be non-negative"):
        call_command("seedheavy", projects=-1, password="secret")

    assert not User.objects.filter(username="heavy").exists()


@pytest.mark.django_db
def test_seedheavy_reads_the_password_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SEEDDB_HEAVY_PASSWORD", "env-password")

    call_command("seedheavy", projects=0, tasks_per_project=0)

    assert User.objects.get(username="heavy").check_password("env-password")


@pytest.mark.django_db
def test_seedheavy_prompts_for_a_password(monkeypatch: pytest.MonkeyPatch) -> None:
    stdin = Mock()
    stdin.isatty.return_value = True
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(getpass, "getpass", lambda prompt: "prompted-password")
    monkeypatch.delenv("SEEDDB_HEAVY_PASSWORD", raising=False)

    call_command("seedheavy", projects=0, tasks_per_project=0)

    assert User.objects.get(username="heavy").check_password("prompted-password")


@pytest.mark.django_db
def test_seedheavy_requires_a_password_without_an_interactive_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdin = Mock()
    stdin.isatty.return_value = False
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.delenv("SEEDDB_HEAVY_PASSWORD", raising=False)

    with pytest.raises(CommandError, match="Provide --password or SEEDDB_HEAVY_PASSWORD"):
        call_command("seedheavy", projects=0, tasks_per_project=0)
