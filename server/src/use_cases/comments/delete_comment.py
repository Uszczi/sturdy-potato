from use_cases.comments._helpers import get_comment_or_404
from use_cases.ports import CommentRepository


class DeleteComment:
    def __init__(self, comments: CommentRepository) -> None:
        self._comments = comments

    async def execute(self, user_id: int, task_id: int, comment_id: int) -> None:
        # Confirm the comment belongs to this task/user (404 otherwise) so the
        # nested delete can't remove a comment addressed under the wrong task.
        await get_comment_or_404(self._comments, user_id, task_id, comment_id)
        await self._comments.delete(user_id, comment_id)
