"""Adapter: a chat turn against a local Ollama model that can call the MCP tools.

This bridges the two external services the API talks to over HTTP — the Ollama
runtime (the model) and the MCP server (the task tools). Neither speaks the
other's protocol, so we list the MCP tools, hand their JSON schemas to Ollama as
function tools, and run the tool-calling loop, streaming events as we go.

The MCP server resolves *who* and *where* from request headers, so the caller's
own access token and workspace id are forwarded on the MCP connection: the model
can only touch what that user could touch.
"""

import json
from collections.abc import AsyncIterator, Sequence
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from ollama import AsyncClient

# Small models need pointed steering: prefer tools over guessing, don't fabricate
# ids. Kept short — every token here competes with a 3B model's budget.
SYSTEM_PROMPT = (
    "You are an assistant for a task board. Use the provided tools to read and "
    "modify tasks instead of guessing. Never invent task ids — call list_tasks "
    "first if you need one. After a tool result, answer the user briefly."
)

# Stop a confused model from looping on tool calls without ever answering.
MAX_TOOL_ROUNDS = 8


def _to_ollama_tools(tools: Sequence[Any]) -> list[dict[str, Any]]:
    """Translate MCP tool descriptors into Ollama's function-tool schema."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools
    ]


def _result_to_text(result: Any) -> str:
    """Reduce an MCP tool result to a string the model can read back."""
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return json.dumps(structured, default=str)
    blocks = getattr(result, "content", None) or []
    texts = [block.text for block in blocks if getattr(block, "text", None)]
    return "\n".join(texts) if texts else "(no output)"


async def _call_tool(mcp: Client[Any], name: str, arguments: dict[str, Any]) -> str:
    try:
        result = await mcp.call_tool(name, arguments)
        return _result_to_text(result)
    except Exception as exc:  # noqa: BLE001 — surface any tool failure to the model
        return f"Error calling {name}: {exc}"


async def stream_chat(
    *,
    ollama_url: str,
    model: str,
    mcp_url: str,
    access_token: str,
    workspace_id: int,
    messages: Sequence[dict[str, str]],
) -> AsyncIterator[dict[str, Any]]:
    """Drive one user turn to a final answer, yielding events for the SSE stream.

    Event shapes (each a JSON object in an SSE ``data:`` field):

    - ``{"type": "token", "text": ...}`` — a piece of the assistant's answer.
    - ``{"type": "tool_call", "name": ..., "arguments": {...}}`` — a tool is run.
    - ``{"type": "tool_result", "name": ...}`` — that tool returned.
    - ``{"type": "done"}`` — the turn is complete.
    """
    ollama = AsyncClient(host=ollama_url)
    transport = StreamableHttpTransport(
        mcp_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Workspace-Id": str(workspace_id),
        },
    )
    convo: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
    ]

    async with Client(transport) as mcp:
        tools = _to_ollama_tools(await mcp.list_tools())

        for _ in range(MAX_TOOL_ROUNDS):
            parts: list[str] = []
            tool_calls: list[Any] = []
            stream = await ollama.chat(
                model=model, messages=convo, tools=tools, stream=True
            )
            async for chunk in stream:
                message = chunk.message
                if message.content:
                    parts.append(message.content)
                    yield {"type": "token", "text": message.content}
                if message.tool_calls:
                    tool_calls.extend(message.tool_calls)

            convo.append(
                {
                    "role": "assistant",
                    "content": "".join(parts),
                    "tool_calls": [call.model_dump() for call in tool_calls] or None,
                }
            )

            if not tool_calls:
                yield {"type": "done"}
                return

            for call in tool_calls:
                name = call.function.name
                arguments = dict(call.function.arguments or {})
                yield {"type": "tool_call", "name": name, "arguments": arguments}
                content = await _call_tool(mcp, name, arguments)
                yield {"type": "tool_result", "name": name}
                convo.append({"role": "tool", "tool_name": name, "content": content})

        yield {"type": "done", "note": "stopped after too many tool rounds"}
