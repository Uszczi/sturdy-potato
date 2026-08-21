"""A minimal Ollama <-> MCP bridge: chat with a local model that can call the task tools.

Ollama is a model runtime, not an MCP client, so this module is the glue in
between. On each turn it:

1. lists the MCP server's tools and translates their JSON schemas into Ollama's
   (OpenAI-style) ``tools`` format;
2. sends the conversation to the model with those tool definitions;
3. if the model emits tool calls, executes them against the MCP server, appends
   the results, and loops until the model answers in plain text.

The MCP server resolves *who* and *where* from request headers (see
:mod:`potato_mcp.context`), so we forward the caller's access token and workspace
id as ``Authorization`` / ``X-Workspace-Id`` on the MCP connection — exactly what
the SPA chat backend would send.

Run it:

    cd mcp && uv run potato-chat

Environment:

- ``OLLAMA_URL``       (default ``http://127.0.0.1:11434``)
- ``OLLAMA_MODEL``     (default ``qwen2.5:3b``)
- ``MCP_URL``          (default ``http://127.0.0.1:8001/mcp``)
- ``MCP_ACCESS_TOKEN`` bearer access JWT for the MCP server (required)
- ``MCP_WORKSPACE_ID`` active workspace id (required)
"""

import asyncio
import json
import os
from collections.abc import Sequence
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from ollama import AsyncClient

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:3b"
DEFAULT_MCP_URL = "http://127.0.0.1:8001/mcp"

# Small models need pointed instructions: prefer tools over guessing, and don't
# invent ids. Keep this short — every token here competes with the 3B's budget.
SYSTEM_PROMPT = (
    "You are an assistant for a task board. Use the provided tools to read and "
    "modify tasks instead of guessing. Never invent task ids — call list_tasks "
    "first if you need one. After a tool result, answer the user in plain, brief "
    "language."
)

# Guard against a model that loops on tool calls without ever answering.
MAX_TOOL_ROUNDS = 8


def _mcp_client() -> Client:
    """An MCP client that forwards the caller's identity as request headers."""
    token = os.environ.get("MCP_ACCESS_TOKEN")
    workspace = os.environ.get("MCP_WORKSPACE_ID")
    if not token or not workspace:
        raise SystemExit(
            "Set MCP_ACCESS_TOKEN and MCP_WORKSPACE_ID (the MCP server resolves "
            "the caller and workspace from these)."
        )
    url = os.environ.get("MCP_URL", DEFAULT_MCP_URL)
    transport = StreamableHttpTransport(
        url,
        headers={"Authorization": f"Bearer {token}", "X-Workspace-Id": workspace},
    )
    return Client(transport)


def _to_ollama_tools(tools: list[Any]) -> list[dict[str, Any]]:
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
    """Reduce an MCP tool result to a string the model can read.

    Prefer the structured JSON payload; fall back to concatenated text blocks.
    """
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return json.dumps(structured, default=str)
    blocks = getattr(result, "content", None) or []
    texts = [block.text for block in blocks if getattr(block, "text", None)]
    return "\n".join(texts) if texts else "(no output)"


async def _run_tool_calls(
    mcp: Client, tool_calls: Sequence[Any]
) -> list[dict[str, str]]:
    """Execute each tool call against the MCP server, one message per result."""
    messages: list[dict[str, str]] = []
    for call in tool_calls:
        name = call.function.name
        args = call.function.arguments or {}
        try:
            result = await mcp.call_tool(name, dict(args))
            content = _result_to_text(result)
        except Exception as exc:  # noqa: BLE001 — surface any tool failure to the model
            content = f"Error calling {name}: {exc}"
        messages.append({"role": "tool", "tool_name": name, "content": content})
    return messages


async def chat_once(
    ollama: AsyncClient,
    mcp: Client,
    model: str,
    tools: list[dict[str, Any]],
    messages: list[dict[str, Any]],
) -> str:
    """Drive one user turn to a final text answer, running tools as requested."""
    for _ in range(MAX_TOOL_ROUNDS):
        response = await ollama.chat(model=model, messages=messages, tools=tools)
        message = response.message
        messages.append(message.model_dump())

        if not message.tool_calls:
            return message.content or ""

        messages.extend(await _run_tool_calls(mcp, message.tool_calls))

    return "Stopped after too many tool calls without a final answer."


async def _repl() -> None:
    model = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    ollama = AsyncClient(host=os.environ.get("OLLAMA_URL", DEFAULT_OLLAMA_URL))

    async with _mcp_client() as mcp:
        tools = _to_ollama_tools(await mcp.list_tools())
        print(
            f"Connected. model={model}  tools={[t['function']['name'] for t in tools]}"
        )
        print("Type a message (Ctrl-D or 'exit' to quit).\n")

        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        while True:
            try:
                user = input("you> ").strip()
            except EOFError:
                print()
                return
            if user in {"exit", "quit"}:
                return
            if not user:
                continue
            messages.append({"role": "user", "content": user})
            answer = await chat_once(ollama, mcp, model, tools, messages)
            print(f"bot> {answer}\n")


def main() -> None:
    try:
        asyncio.run(_repl())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
