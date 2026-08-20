from use_cases.entities import Comment
from use_cases.ports import CommentRepository, TaskRepository
from use_cases.tasks._helpers import get_task_or_404


class ListComments:
    def __init__(self, comments: CommentRepository, tasks: TaskRepository) -> None:
        self._comments = comments
        self._tasks = tasks

    async def execute(self, user_id: int, task_id: int) -> list[Comment]:
        # 404 on an unknown/foreign task before revealing an empty thread.
        await get_task_or_404(self._tasks, user_id, task_id)
        return await self._comments.list_for_task(user_id, task_id)
