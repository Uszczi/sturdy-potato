"""Shared fetch-and-validate helpers used by several comment use cases."""

from use_cases.entities import Comment
from use_cases.exceptions import CommentNotFound
from use_cases.ports import CommentRepository


async def get_comment_or_404(
    comments: CommentRepository, user_id: int, task_id: int, comment_id: int
) -> Comment:
    comment = await comments.get(user_id, comment_id)
    # Scope the comment to the task in the URL so a mismatched pair 404s rather
    # than editing a comment that lives under a different task.
    if comment is None or comment.task_id != task_id:
        raise CommentNotFound()
    return comment
