from use_cases.dtos import CommentCreateData
from use_cases.entities import Comment
from use_cases.ports import CommentRepository, TaskRepository
from use_cases.tasks._helpers import get_task_or_404


class CreateComment:
    def __init__(self, comments: CommentRepository, tasks: TaskRepository) -> None:
        self._comments = comments
        self._tasks = tasks

    async def execute(
        self, workspace_id: int, user_id: int, task_id: int, data: CommentCreateData
    ) -> Comment:
        await get_task_or_404(self._tasks, workspace_id, task_id)
        return await self._comments.create(workspace_id, task_id, user_id, data)
