"""The chat endpoint: authorization, and relaying adapter events as SSE.

The model and the MCP server live behind ``stream_chat`` (covered in
tests/infrastructure/test_llm.py), so it is replaced here with a canned event
stream: what is under test is the route's authorization and how it maps those
events onto the SSE wire.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.routes.chat as chat_route
from auth import get_access_token
from tests.factories import auth_headers, create_user, create_user_with_workspace
from use_cases.exceptions import InvalidToken

EVENTS: list[dict[str, Any]] = [
    {"type": "tool_call", "name": "list_tasks", "arguments": {}},
    {"type": "tool_result", "name": "list_tasks"},
    {"type": "token", "text": "You have one task."},
    {"type": "done"},
]


def _stub_stream(
    monkeypatch: pytest.MonkeyPatch, events: list[dict[str, Any]] = EVENTS
) -> list[dict[str, Any]]:
    """Replace the adapter with a canned stream; hand back the kwargs it saw."""
    seen: list[dict[str, Any]] = []

    def fake_stream_chat(**kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        seen.append(kwargs)

        async def stream() -> AsyncIterator[dict[str, Any]]:
            for event in events:
                yield event

        return stream()

    monkeypatch.setattr(chat_route, "stream_chat", fake_stream_chat)
    return seen


async def test_chatting_streams_the_adapters_events_as_sse(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    user, _workspace = await create_user_with_workspace(session)
    _stub_stream(monkeypatch)

    response = await client.post(
        "/api/chat/",
        json={"messages": [{"role": "user", "content": "what's on my plate?"}]},
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    # Each event is named by its type, so the client can dispatch on it.
    assert [
        line for line in response.text.splitlines() if line.startswith("event:")
    ] == [
        "event: tool_call",
        "event: tool_result",
        "event: token",
        "event: done",
    ]
    payloads = [
        json.loads(line.removeprefix("data:").strip())
        for line in response.text.splitlines()
        if line.startswith("data:")
    ]
    assert payloads == EVENTS


async def test_the_conversation_and_the_callers_credentials_reach_the_adapter(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    user, workspace = await create_user_with_workspace(session)
    seen = _stub_stream(monkeypatch)
    headers = auth_headers(user)

    await client.post(
        "/api/chat/",
        json={
            "messages": [
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
                {"role": "user", "content": "and now?"},
            ]
        },
        headers=headers,
    )

    assert seen[0]["workspace_id"] == workspace.id
    # The caller's own token is forwarded, so tools run as that user.
    assert seen[0]["access_token"] == headers["Authorization"].removeprefix("Bearer ")
    assert seen[0]["messages"] == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "and now?"},
    ]


async def test_a_non_member_cannot_chat_in_a_workspace(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, workspace = await create_user_with_workspace(session)
    stranger = await create_user(session)
    seen = _stub_stream(monkeypatch)

    response = await client.post(
        "/api/chat/",
        json={"messages": [{"role": "user", "content": "hi"}]},
        headers=auth_headers(stranger, workspace),
    )

    # Membership never leaks a workspace's existence, and the model never runs.
    assert response.status_code == 404
    assert seen == []


async def test_chatting_rejects_an_empty_conversation(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    user, _workspace = await create_user_with_workspace(session)
    _stub_stream(monkeypatch)

    response = await client.post(
        "/api/chat/",
        json={"messages": []},
        headers=auth_headers(user),
    )

    assert response.status_code == 422


async def test_the_forwarded_token_dependency_rejects_a_missing_header() -> None:
    # Routes resolve the workspace (and so the user) first, so this dependency's
    # own guard is unreachable through the API; it is still the contract that
    # keeps an unauthenticated request from reaching the MCP server.
    with pytest.raises(InvalidToken):
        await get_access_token(None)
