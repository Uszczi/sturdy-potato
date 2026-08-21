"""Direct repository tests for branches the use cases guard against reaching.

Use cases pre-check existence before calling ``update``, so the repository's
"row not found" return is unreachable through the API. It is still part of the
port contract (the fakes honour it), so exercise it directly here.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.repositories import CommentRepository, TaskRepository


async def test_update_returns_none_for_a_missing_task(session: AsyncSession) -> None:
    repository = TaskRepository(session)

    result = await repository.update(user_id=1, task_id=999, changes={"title": "x"})

    assert result is None


async def test_set_positions_with_an_empty_map_is_a_noop(
    session: AsyncSession,
) -> None:
    # MoveTask always renumbers at least the moved card, so the empty short-cut
    # is unreachable through the API; exercise it directly.
    repository = TaskRepository(session)

    await repository.set_positions(user_id=1, positions={})


async def test_comment_update_returns_none_for_a_missing_comment(
    session: AsyncSession,
) -> None:
    repository = CommentRepository(session)

    result = await repository.update(user_id=1, comment_id=999, changes={"body": "x"})

    assert result is None


async def test_comment_delete_returns_false_for_a_missing_comment(
    session: AsyncSession,
) -> None:
    repository = CommentRepository(session)

    assert await repository.delete(user_id=1, comment_id=999) is False
