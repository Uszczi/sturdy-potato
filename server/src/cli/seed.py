import os
import random
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select

from auth import hash_password
from infrastructure.db import async_session_maker
from infrastructure.models import Project, Todo, User

DEMO_USERNAME = os.environ.get("SEEDDB_DEMO_USERNAME", "demo")
DEMO_PASSWORD = os.environ.get("SEEDDB_DEMO_PASSWORD", "demo-password-123")

ADMIN_USERNAME = os.environ.get("SEEDDB_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("SEEDDB_ADMIN_PASSWORD", "admin-password-123")

HEAVY_USERNAME = os.environ.get("SEEDDB_HEAVY_USERNAME", "heavy")
HEAVY_PASSWORD = os.environ.get("SEEDDB_HEAVY_PASSWORD", "heavy-password-123")

# Accent colours handed to the demo projects in order, matching the presets the
# client offers.
_SEED_COLORS: tuple[str, ...] = ("#6366f1", "#10b981", "#f97316")

SEEDED_PROJECTS: tuple[tuple[str, tuple[tuple[str, str, bool], ...]], ...] = (
    (
        "Getting started",
        (
            (
                "Explore the todo list",
                "Review the seeded tasks and mark one complete.",
                False,
            ),
            ("Create your first task", "Use the API to add a task.", False),
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
            ("Tidy the inbox", "Give every loose task a useful next step.", False),
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
            ("Invite early testers", "Ask a small group for focused feedback.", False),
            (
                "Schedule launch review",
                "Set aside time to review the final readiness checklist.",
                False,
            ),
        ),
    ),
)


async def _get_or_create_demo_user(
    session: AsyncSession,
    username: str = DEMO_USERNAME,
    password: str = DEMO_PASSWORD,
) -> tuple[User, bool]:
    user = await session.scalar(select(User).where(User.username == username))
    if user is not None:
        return user, False
    user = User(
        username=username,
        hashed_password=hash_password(password),
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def _seed_projects_and_todos(session: AsyncSession, user: User) -> None:
    for project_position, (project_name, todos) in enumerate(SEEDED_PROJECTS):
        project = await session.scalar(
            select(Project).where(
                Project.user_id == user.id, Project.name == project_name
            )
        )
        if project is None:
            project = Project(
                user_id=user.id,
                name=project_name,
                color=_SEED_COLORS[project_position % len(_SEED_COLORS)],
                position=project_position,
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
        for task_position, (title, description, completed) in enumerate(todos):
            existing = await session.scalar(
                select(Todo).where(
                    Todo.user_id == user.id,
                    Todo.project_id == project.id,
                    Todo.title == title,
                )
            )
            if existing is None:
                session.add(
                    Todo(
                        user_id=user.id,
                        project_id=project.id,
                        title=title,
                        description=description,
                        completed=completed,
                        position=task_position,
                    )
                )
        await session.commit()


async def seed_demo_user(
    username: str = DEMO_USERNAME,
    password: str = DEMO_PASSWORD,
    session_maker: async_sessionmaker[AsyncSession] = async_session_maker,
) -> None:
    async with session_maker() as session:
        user, created = await _get_or_create_demo_user(session, username, password)
        status = "Created" if created else "Found"
        print(f"{status} demo user '{user.username}'.")


async def seed(
    session_maker: async_sessionmaker[AsyncSession] = async_session_maker,
) -> None:
    async with session_maker() as session:
        user, created = await _get_or_create_demo_user(session)
        await _seed_projects_and_todos(session, user)
        status = "Created" if created else "Found"
        print(f"{status} demo user '{user.username}'.")


def _heavy_task_counts(project_count: int, max_tasks: int) -> list[int]:
    """Task counts per project, ramping linearly from 1 up to max_tasks."""
    if project_count == 1:
        return [max_tasks]
    return [
        round(1 + index * (max_tasks - 1) / (project_count - 1))
        for index in range(project_count)
    ]


def _random_due_date(rng: random.Random, today: date) -> date | None:
    """A due date spread around today, with ~30% of tasks left undated."""
    if rng.random() < 0.3:
        return None
    return today + timedelta(days=rng.randint(-14, 45))


async def seed_heavy(
    username: str = HEAVY_USERNAME,
    password: str = HEAVY_PASSWORD,
    project_count: int = 100,
    max_tasks: int = 1000,
    completed_ratio: float = 0.3,
    seed: int = 0,
    session_maker: async_sessionmaker[AsyncSession] = async_session_maker,
) -> None:
    counts = _heavy_task_counts(project_count, max_tasks)
    rng = random.Random(seed)
    today = datetime.now(UTC).date()
    completed_total = 0
    async with session_maker() as session:
        user, _ = await _get_or_create_demo_user(session, username, password)
        already_seeded = await session.scalar(
            select(Project.id).where(Project.user_id == user.id)
        )
        if already_seeded is not None:
            print(f"Heavy user '{user.username}' already has projects; skipping.")
            return
        for position, task_count in enumerate(counts):
            project = Project(
                user_id=user.id, name=f"Project {position + 1}", position=position
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            tasks = []
            for number in range(task_count):
                completed = rng.random() < completed_ratio
                completed_total += completed
                tasks.append(
                    Todo(
                        user_id=user.id,
                        project_id=project.id,
                        title=f"Task {number + 1}",
                        position=number,
                        completed=completed,
                        due_date=_random_due_date(rng, today),
                    )
                )
            session.add_all(tasks)
            await session.commit()
        print(
            f"Seeded heavy user '{user.username}' with {project_count} projects "
            f"and {sum(counts)} tasks ({completed_total} completed)."
        )


async def seed_admin(
    username: str = ADMIN_USERNAME,
    password: str = ADMIN_PASSWORD,
    session_maker: async_sessionmaker[AsyncSession] = async_session_maker,
) -> None:
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(
                username=username,
                hashed_password=hash_password(password),
                is_active=True,
                is_staff=True,
            )
            status = "Created"
        else:
            # Promote an existing account so re-running is safe.
            user.is_active = True
            user.is_staff = True
            status = "Promoted"
        session.add(user)
        await session.commit()
        print(f"{status} admin user '{username}'.")
