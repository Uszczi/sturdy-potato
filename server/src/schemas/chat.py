from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Only the two roles the client owns; the system prompt is added server-side
    # and tool turns are produced by the loop, never sent by the browser.
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The full conversation so far (the client keeps the history and replays it).
    messages: Annotated[list[ChatMessageInput], Field(min_length=1, max_length=50)]
