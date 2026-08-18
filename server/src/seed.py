import asyncio
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select

from auth import hash_password
from db import async_session_maker
from models import Project, Todo, User

DEMO_USERNAME = os.environ.get("SEEDDB_DEMO_USERNAME", "demo")
DEMO_PASSWORD = os.environ.get("SEEDDB_DEMO_PASSWORD", "demo-password-123")

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


async def _get_or_create_demo_user(session: AsyncSession) -> tuple[User, bool]:
    user = await session.scalar(select(User).where(User.username == DEMO_USERNAME))
    if user is not None:
        return user, False
    user = User(
        username=DEMO_USERNAME,
        hashed_password=hash_password(DEMO_PASSWORD),
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
                user_id=user.id, name=project_name, position=project_position
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


async def seed(
    session_maker: async_sessionmaker[AsyncSession] = async_session_maker,
) -> None:
    async with session_maker() as session:
        user, created = await _get_or_create_demo_user(session)
        await _seed_projects_and_todos(session, user)
        status = "Created" if created else "Found"
        print(f"{status} demo user '{user.username}'.")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
