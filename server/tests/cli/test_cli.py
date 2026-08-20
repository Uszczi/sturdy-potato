import pytest
from click.testing import CliRunner

from cli import cli
from cli import seed as seed_module


def test_cli_seed_invokes_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = False

    async def fake_seed() -> None:
        nonlocal ran
        ran = True

    monkeypatch.setattr(seed_module, "seed", fake_seed)
    result = CliRunner().invoke(cli, ["seed"])

    assert result.exit_code == 0
    assert ran


def test_cli_create_demo_invokes_seed_demo_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: tuple[str, str] | None = None

    async def fake_seed_demo_user(username: str, password: str) -> None:
        nonlocal captured
        captured = (username, password)

    monkeypatch.setattr(seed_module, "seed_demo_user", fake_seed_demo_user)
    result = CliRunner().invoke(
        cli,
        ["create-demo", "--username", "visitor", "--password", "secret"],
    )

    assert result.exit_code == 0
    assert captured == ("visitor", "secret")


def test_cli_create_heavy_invokes_seed_heavy(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: tuple[str, str, int, int, float, int] | None = None

    async def fake_seed_heavy(
        username: str,
        password: str,
        projects: int,
        max_tasks: int,
        completed_ratio: float,
        seed: int,
    ) -> None:
        nonlocal captured
        captured = (username, password, projects, max_tasks, completed_ratio, seed)

    monkeypatch.setattr(seed_module, "seed_heavy", fake_seed_heavy)
    result = CliRunner().invoke(
        cli,
        [
            "create-heavy",
            "--projects",
            "3",
            "--max-tasks",
            "5",
            "--completed-ratio",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    assert captured == (
        seed_module.HEAVY_USERNAME,
        seed_module.HEAVY_PASSWORD,
        3,
        5,
        0.5,
        0,
    )


def test_cli_create_admin_invokes_seed_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: tuple[str, str] | None = None

    async def fake_seed_admin(username: str, password: str) -> None:
        nonlocal captured
        captured = (username, password)

    monkeypatch.setattr(seed_module, "seed_admin", fake_seed_admin)
    result = CliRunner().invoke(
        cli,
        ["create-admin", "--username", "boss", "--password", "secret"],
    )

    assert result.exit_code == 0
    assert captured == ("boss", "secret")
