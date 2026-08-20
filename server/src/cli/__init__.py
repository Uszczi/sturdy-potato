import asyncio

import click

from cli import seed as seed_module


@click.group()
def cli() -> None:
    """Sturdy Potato management commands."""


@cli.command("seed")
def seed_command() -> None:
    """Seed the demo user with example projects and tasks."""
    asyncio.run(seed_module.seed())


@cli.command("create-demo")
@click.option("--username", default=seed_module.DEMO_USERNAME, show_default=True)
@click.option("--password", default=seed_module.DEMO_PASSWORD, show_default=True)
def create_demo_command(username: str, password: str) -> None:
    """Create the demo user without seeding projects or tasks."""
    asyncio.run(seed_module.seed_demo_user(username, password))


@cli.command("create-heavy")
@click.option("--username", default=seed_module.HEAVY_USERNAME, show_default=True)
@click.option("--password", default=seed_module.HEAVY_PASSWORD, show_default=True)
@click.option("--projects", default=100, show_default=True)
@click.option("--max-tasks", default=1000, show_default=True)
@click.option(
    "--completed-ratio",
    type=click.FloatRange(0.0, 1.0),
    default=0.3,
    show_default=True,
    help="Fraction of tasks marked completed.",
)
@click.option(
    "--seed", default=0, show_default=True, help="Seed for reproducible random data."
)
def create_heavy_command(
    username: str,
    password: str,
    projects: int,
    max_tasks: int,
    completed_ratio: float,
    seed: int,
) -> None:
    """Seed a heavy user with many projects and a growing pile of tasks."""
    asyncio.run(
        seed_module.seed_heavy(
            username, password, projects, max_tasks, completed_ratio, seed
        )
    )


@cli.command("create-admin")
@click.option("--username", default=seed_module.ADMIN_USERNAME, show_default=True)
@click.option(
    "--password",
    default=seed_module.ADMIN_PASSWORD,
    required=seed_module.ADMIN_PASSWORD is None,
    show_default=False,
    help="Required (or set SEEDDB_ADMIN_PASSWORD); no default is provided.",
)
def create_admin_command(username: str, password: str) -> None:
    """Create or promote an active staff user for the /admin panel."""
    asyncio.run(seed_module.seed_admin(username, password))


__all__ = ["cli"]
