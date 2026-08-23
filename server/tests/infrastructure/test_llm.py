"""The Ollama + MCP chat adapter, driven against stand-ins for both services.

``stream_chat`` is the only place the two external protocols meet, so the fakes
here mimic just the surface it touches: an Ollama client that streams chunks
carrying content and tool calls, and an MCP client that lists tools and runs
them. That keeps the tool-calling loop testable without a model or a server.
"""

from collections.abc import AsyncIterator, Sequence
from typing import Any, Self

import pytest

from infrastructure import llm
from infrastructure.llm import MAX_TOOL_ROUNDS, SYSTEM_PROMPT, stream_chat


class FakeTool:
    """An MCP tool descriptor, as ``list_tools`` returns them."""

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description
        self.inputSchema = {"type": "object", "properties": {}}


class FakeFunction:
    def __init__(self, name: str, arguments: dict[str, Any] | None) -> None:
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, name: str, arguments: dict[str, Any] | None = None) -> None:
        self.function = FakeFunction(name, arguments)

    def model_dump(self) -> dict[str, Any]:
        return {
            "function": {
                "name": self.function.name,
                "arguments": self.function.arguments,
            }
        }


class FakeMessage:
    def __init__(
        self, content: str = "", tool_calls: list[FakeToolCall] | None = None
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls


class FakeChunk:
    def __init__(self, message: FakeMessage) -> None:
        self.message = message


class FakeOllama:
    """Replays one canned list of chunks per chat round, recording the calls."""

    def __init__(self, rounds: Sequence[Sequence[FakeChunk]]) -> None:
        self._rounds = list(rounds)
        self.calls: list[dict[str, Any]] = []

    async def chat(self, **kwargs: Any) -> AsyncIterator[FakeChunk]:
        # The adapter appends to one conversation list as it goes, so snapshot it
        # to record what each round actually saw.
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        # A model that keeps calling tools reuses its last round forever, which
        # is what drives the MAX_TOOL_ROUNDS guard.
        chunks = self._rounds[min(len(self.calls) - 1, len(self._rounds) - 1)]

        async def stream() -> AsyncIterator[FakeChunk]:
            for chunk in chunks:
                yield chunk

        return stream()


class FakeMcp:
    def __init__(
        self,
        tools: Sequence[FakeTool],
        results: dict[str, Any] | None = None,
    ) -> None:
        self._tools = list(tools)
        self._results = results or {}
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def list_tools(self) -> list[FakeTool]:
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        self.calls.append((name, arguments))
        result = self._results[name]
        if isinstance(result, Exception):
            raise result
        return result


class FakeResult:
    def __init__(self, structured: Any = None, content: Any = None) -> None:
        self.structured_content = structured
        self.content = content


class FakeBlock:
    def __init__(self, text: str | None) -> None:
        self.text = text


def _install(
    monkeypatch: pytest.MonkeyPatch, ollama: FakeOllama, mcp: FakeMcp
) -> list[dict[str, Any]]:
    """Point the adapter at the fakes; hand back the recorded transport headers."""
    transports: list[dict[str, Any]] = []

    def fake_transport(url: str, headers: dict[str, str]) -> dict[str, Any]:
        transport = {"url": url, "headers": headers}
        transports.append(transport)
        return transport

    monkeypatch.setattr(llm, "AsyncClient", lambda host: ollama)
    monkeypatch.setattr(llm, "StreamableHttpTransport", fake_transport)
    monkeypatch.setattr(llm, "Client", lambda transport: mcp)
    return transports


async def _run(**kwargs: Any) -> list[dict[str, Any]]:
    defaults: dict[str, Any] = {
        "ollama_url": "http://ollama",
        "model": "test-model",
        "mcp_url": "http://mcp/mcp",
        "access_token": "token-abc",
        "workspace_id": 7,
        "messages": [{"role": "user", "content": "hi"}],
    }
    return [event async for event in stream_chat(**{**defaults, **kwargs})]


async def test_a_plain_answer_streams_tokens_then_done(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama([[FakeChunk(FakeMessage("Hel")), FakeChunk(FakeMessage("lo"))]])
    _install(monkeypatch, ollama, FakeMcp([]))

    events = await _run()

    assert events == [
        {"type": "token", "text": "Hel"},
        {"type": "token", "text": "lo"},
        {"type": "done"},
    ]


async def test_the_system_prompt_precedes_the_replayed_conversation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama([[FakeChunk(FakeMessage("ok"))]])
    _install(monkeypatch, ollama, FakeMcp([]))

    await _run(messages=[{"role": "user", "content": "hi"}])

    assert ollama.calls[0]["messages"] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "hi"},
    ]


async def test_the_callers_credentials_are_forwarded_to_the_mcp_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama([[FakeChunk(FakeMessage("ok"))]])
    transports = _install(monkeypatch, ollama, FakeMcp([]))

    await _run(access_token="token-abc", workspace_id=7)

    # The model's tool calls run as the caller, so its token and workspace ride
    # along on the MCP connection.
    assert transports[0]["url"] == "http://mcp/mcp"
    assert transports[0]["headers"] == {
        "Authorization": "Bearer token-abc",
        "X-Workspace-Id": "7",
    }


async def test_mcp_tools_are_offered_to_the_model_as_function_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama([[FakeChunk(FakeMessage("ok"))]])
    tools = [FakeTool("list_tasks", "List them"), FakeTool("create_task")]
    _install(monkeypatch, ollama, FakeMcp(tools))

    await _run()

    assert ollama.calls[0]["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List them",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_task",
                # A tool with no description still needs the key present.
                "description": "",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


async def test_a_tool_call_is_announced_run_and_fed_back_to_the_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama(
        [
            [FakeChunk(FakeMessage(tool_calls=[FakeToolCall("list_tasks", {"n": 1})]))],
            [FakeChunk(FakeMessage("You have one task."))],
        ]
    )
    mcp = FakeMcp(
        [FakeTool("list_tasks")], {"list_tasks": FakeResult(structured={"count": 1})}
    )
    _install(monkeypatch, ollama, mcp)

    events = await _run()

    assert events == [
        {"type": "tool_call", "name": "list_tasks", "arguments": {"n": 1}},
        {"type": "tool_result", "name": "list_tasks"},
        {"type": "token", "text": "You have one task."},
        {"type": "done"},
    ]
    assert mcp.calls == [("list_tasks", {"n": 1})]
    # The second round sees the assistant's tool call and the tool's output.
    assert ollama.calls[1]["messages"][-1] == {
        "role": "tool",
        "tool_name": "list_tasks",
        "content": '{"count": 1}',
    }


async def test_a_tool_call_without_arguments_becomes_an_empty_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama(
        [
            [FakeChunk(FakeMessage(tool_calls=[FakeToolCall("count_tasks", None)]))],
            [FakeChunk(FakeMessage("Two."))],
        ]
    )
    mcp = FakeMcp([FakeTool("count_tasks")], {"count_tasks": FakeResult(structured=2)})
    _install(monkeypatch, ollama, mcp)

    events = await _run()

    assert events[0] == {"type": "tool_call", "name": "count_tasks", "arguments": {}}
    assert mcp.calls == [("count_tasks", {})]


async def test_an_unstructured_tool_result_falls_back_to_its_text_blocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama(
        [
            [FakeChunk(FakeMessage(tool_calls=[FakeToolCall("list_tasks", {})]))],
            [FakeChunk(FakeMessage("done"))],
        ]
    )
    mcp = FakeMcp(
        [FakeTool("list_tasks")],
        {
            "list_tasks": FakeResult(
                content=[FakeBlock("first"), FakeBlock(None), FakeBlock("second")]
            )
        },
    )
    _install(monkeypatch, ollama, mcp)

    await _run()

    assert ollama.calls[1]["messages"][-1]["content"] == "first\nsecond"


async def test_an_empty_tool_result_reads_back_as_no_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama(
        [
            [FakeChunk(FakeMessage(tool_calls=[FakeToolCall("list_tasks", {})]))],
            [FakeChunk(FakeMessage("done"))],
        ]
    )
    mcp = FakeMcp([FakeTool("list_tasks")], {"list_tasks": FakeResult()})
    _install(monkeypatch, ollama, mcp)

    await _run()

    assert ollama.calls[1]["messages"][-1]["content"] == "(no output)"


async def test_a_failing_tool_reports_the_error_to_the_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama(
        [
            [
                FakeChunk(
                    FakeMessage(tool_calls=[FakeToolCall("delete_task", {"id": 1})])
                )
            ],
            [FakeChunk(FakeMessage("I could not do that."))],
        ]
    )
    mcp = FakeMcp([FakeTool("delete_task")], {"delete_task": RuntimeError("boom")})
    _install(monkeypatch, ollama, mcp)

    events = await _run()

    # The turn continues: the model is told what went wrong and answers anyway.
    assert {"type": "tool_result", "name": "delete_task"} in events
    assert (
        ollama.calls[1]["messages"][-1]["content"] == "Error calling delete_task: boom"
    )


async def test_a_model_that_never_stops_calling_tools_is_cut_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = FakeOllama(
        [[FakeChunk(FakeMessage(tool_calls=[FakeToolCall("list_tasks", {})]))]]
    )
    mcp = FakeMcp([FakeTool("list_tasks")], {"list_tasks": FakeResult(structured=[])})
    _install(monkeypatch, ollama, mcp)

    events = await _run()

    assert len(ollama.calls) == MAX_TOOL_ROUNDS
    assert events[-1] == {"type": "done", "note": "stopped after too many tool rounds"}
