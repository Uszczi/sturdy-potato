from use_cases.comments._helpers import get_comment_or_404
from use_cases.dtos import CommentUpdateData
from use_cases.entities import Comment
from use_cases.ports import CommentRepository


class UpdateComment:
    def __init__(self, comments: CommentRepository) -> None:
        self._comments = comments

    async def execute(
        self, user_id: int, task_id: int, comment_id: int, data: CommentUpdateData
    ) -> Comment:
        await get_comment_or_404(self._comments, user_id, task_id, comment_id)
        comment = await self._comments.update(user_id, comment_id, {"body": data.body})
        assert comment is not None  # existence checked above, same transaction
        return comment
