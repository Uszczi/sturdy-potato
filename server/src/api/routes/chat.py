from collections.abc import AsyncIterable

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

from auth import AccessToken, WorkspaceId
from config import settings
from infrastructure.llm import stream_chat
from schemas.chat import ChatRequest

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["chat"])


@router.post("/", response_class=EventSourceResponse, operation_id="api_chat_create")
async def chat(
    body: ChatRequest,
    workspace_id: WorkspaceId,
    access_token: AccessToken,
) -> AsyncIterable[ServerSentEvent]:
    """Chat with the local model, streaming tokens and tool activity as SSE.

    The conversation is replayed by the client on each turn. Authorization is the
    normal workspace-membership check; the caller's token is forwarded to the MCP
    server so the model's tool calls run as that user.
    """
    events = stream_chat(
        ollama_url=settings.ollama_url,
        model=settings.ollama_model,
        mcp_url=settings.mcp_url,
        access_token=access_token,
        workspace_id=workspace_id,
        messages=[message.model_dump() for message in body.messages],
    )
    async for event in events:
        yield ServerSentEvent(data=event, event=event["type"])
