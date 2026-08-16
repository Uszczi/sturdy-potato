import getpass
import sys
from io import StringIO
from unittest.mock import Mock

import pytest
from django.core.management import CommandError, call_command

from infrastructure.models import Project, Todo, User


@pytest.mark.django_db
def test_seeddb_creates_superuser_demo_user_and_todos() -> None:
    output = StringIO()

    call_command(
        "seeddb",
        superuser_password="admin-password",
        demo_password="demo-password",
        stdout=output,
    )

    superuser = User.objects.get(username="admin")
    demo_user = User.objects.get(username="demo")

    assert superuser.email == "admin@example.com"
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.check_password("admin-password")
    assert demo_user.email == "demo@example.com"
    assert demo_user.check_password("demo-password")
    projects = list(
        Project.objects.filter(user=demo_user)
        .order_by("position")
        .values_list("name", flat=True)
    )
    assert projects == ["Getting started", "Weekly planning", "Product launch"]
    assert [
        Todo.objects.filter(user=demo_user, project__name=name).count()
        for name in projects
    ] == [3, 4, 5]
    assert Todo.objects.filter(user=demo_user).count() == 12
    assert "Created superuser 'admin'." in output.getvalue()
    assert "Created demo user 'demo'." in output.getvalue()
    assert "Created 3 new demo project(s)." in output.getvalue()
    assert "Created 12 new demo todo(s)." in output.getvalue()


@pytest.mark.django_db
def test_seeddb_is_idempotent_and_does_not_reset_existing_passwords() -> None:
    call_command(
        "seeddb",
        superuser_password="original-admin-password",
        demo_password="original-demo-password",
    )
    demo_user = User.objects.get(username="demo")
    Todo.objects.filter(user=demo_user, title="Explore the todo list").update(
        description="A local customization"
    )

    output = StringIO()
    call_command(
        "seeddb",
        superuser_password="new-admin-password",
        demo_password="new-demo-password",
        stdout=output,
    )

    assert User.objects.filter(username="admin").count() == 1
    assert User.objects.filter(username="demo").count() == 1
    assert Project.objects.filter(user=demo_user).count() == 3
    assert Todo.objects.filter(user=demo_user).count() == 12
    assert User.objects.get(username="admin").check_password("original-admin-password")
    assert User.objects.get(username="demo").check_password("original-demo-password")
    assert (
        Todo.objects.get(user=demo_user, title="Explore the todo list").description
        == "A local customization"
    )
    assert "Found superuser 'admin'." in output.getvalue()
    assert "Found demo user 'demo'." in output.getvalue()
    assert "Created 0 new demo project(s)." in output.getvalue()
    assert "Created 0 new demo todo(s)." in output.getvalue()


@pytest.mark.django_db
def test_seeddb_can_skip_demo_data() -> None:
    call_command(
        "seeddb",
        superuser_password="admin-password",
        skip_demo_data=True,
    )

    assert User.objects.filter(username="admin").exists()
    assert not User.objects.filter(username="demo").exists()
    assert not Project.objects.exists()
    assert not Todo.objects.exists()


@pytest.mark.django_db
def test_seeddb_reads_passwords_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SEEDDB_SUPERUSER_PASSWORD", "admin-password")
    monkeypatch.setenv("SEEDDB_DEMO_PASSWORD", "demo-password")

    call_command("seeddb")

    assert User.objects.get(username="admin").check_password("admin-password")
    assert User.objects.get(username="demo").check_password("demo-password")


@pytest.mark.django_db
def test_seeddb_prompts_for_passwords(monkeypatch: pytest.MonkeyPatch) -> None:
    stdin = Mock()
    stdin.isatty.return_value = True
    passwords = iter(("admin-password", "demo-password"))
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(getpass, "getpass", lambda prompt: next(passwords))

    call_command("seeddb")

    assert User.objects.get(username="admin").check_password("admin-password")
    assert User.objects.get(username="demo").check_password("demo-password")


@pytest.mark.django_db
def test_seeddb_requires_a_password_without_an_interactive_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdin = Mock()
    stdin.isatty.return_value = False
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.delenv("SEEDDB_SUPERUSER_PASSWORD", raising=False)

    with pytest.raises(CommandError, match="Provide --superuser-password"):
        call_command("seeddb", skip_demo_data=True)


@pytest.mark.django_db
def test_seeddb_rejects_an_existing_non_superuser_with_the_seeded_username() -> None:
    User.objects.create_user(username="admin", password="existing-password")

    with pytest.raises(CommandError, match="already exists but is not a superuser"):
        call_command("seeddb", skip_demo_data=True)


@pytest.mark.django_db
def test_seeddb_repairs_an_inactive_existing_superuser() -> None:
    User.objects.create_user(
        username="admin",
        password="existing-password",
        is_active=False,
        is_staff=False,
        is_superuser=True,
    )

    call_command("seeddb", skip_demo_data=True)

    superuser = User.objects.get(username="admin")
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.check_password("existing-password")


@pytest.mark.django_db
def test_seeddb_requires_distinct_superuser_and_demo_usernames() -> None:
    with pytest.raises(CommandError, match="must have different usernames"):
        call_command(
            "seeddb",
            superuser_username="same-user",
            demo_username="same-user",
            superuser_password="admin-password",
            demo_password="demo-password",
        )

    assert not User.objects.filter(username="same-user").exists()
