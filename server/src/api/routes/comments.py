from fastapi import APIRouter, status

from api.dependencies import (
    CreateCommentDep,
    DeleteCommentDep,
    ListCommentsDep,
    UpdateCommentDep,
)
from auth import CurrentUserId
from schemas.comment import CommentCreateInput, CommentSchema, CommentUpdateInput

# Comments hang off a task, so the whole router is nested under its id.
router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


@router.get("/", operation_id="api_task_comments_list")
async def list_comments(
    task_id: int, user_id: CurrentUserId, use_case: ListCommentsDep
) -> list[CommentSchema]:
    comments = await use_case.execute(user_id, task_id)
    return [CommentSchema.model_validate(comment) for comment in comments]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    operation_id="api_task_comments_create",
)
async def create_comment(
    task_id: int,
    body: CommentCreateInput,
    user_id: CurrentUserId,
    use_case: CreateCommentDep,
) -> CommentSchema:
    comment = await use_case.execute(user_id, task_id, body.to_domain())
    return CommentSchema.model_validate(comment)


@router.patch("/{comment_id}/", operation_id="api_task_comments_partial_update")
async def update_comment(
    task_id: int,
    comment_id: int,
    body: CommentUpdateInput,
    user_id: CurrentUserId,
    use_case: UpdateCommentDep,
) -> CommentSchema:
    comment = await use_case.execute(user_id, task_id, comment_id, body.to_domain())
    return CommentSchema.model_validate(comment)


@router.delete(
    "/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="api_task_comments_destroy",
)
async def delete_comment(
    task_id: int,
    comment_id: int,
    user_id: CurrentUserId,
    use_case: DeleteCommentDep,
) -> None:
    await use_case.execute(user_id, task_id, comment_id)
