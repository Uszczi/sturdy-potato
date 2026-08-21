# potato-mcp

A [FastMCP](https://gofastmcp.com) server that exposes the sturdy-potato **task**
use cases as MCP tools over **streamable HTTP** or **stdio**. It calls the
server's `use_cases` layer in-process (no HTTP hop to the API), reusing the same
repositories, `config`, and JWT verification.

## How identity works

The server has no session of its own. Each tool call resolves *who* and *where*,
mirroring the REST API:

- **User** — a bearer access token, decoded with the same
  `token_service`/`GetCurrentUser` the API uses.
- **Workspace** — a workspace id, validated against the caller's membership
  (`WorkspaceRepository.is_member`), exactly like the API's `{workspace_id}` path
  segment.

Where these come from depends on the transport:

| Transport | User | Workspace |
| --- | --- | --- |
| HTTP  | `Authorization: Bearer <access-jwt>` header | `X-Workspace-Id: <id>` header |
| stdio | `MCP_ACCESS_TOKEN` env | `MCP_WORKSPACE_ID` env |

Over HTTP the intended client is the React SPA's chat backend, which forwards the
logged-in user's access token and their active workspace id on every request.
Over stdio a client launches the process directly, passing the token and
workspace id through its environment.

> **Config must match the API.** Verification uses `config.settings`, so the MCP
> process must share the API's `SECRET_KEY` (to verify JWTs) and `DATABASE_URL`
> (to read the data). In local dev both default to the same values, so it works
> out of the box once Postgres is up.

## Run

From the repo root (Postgres must be running — `just db`):

```bash
just mcp                 # HTTP → http://127.0.0.1:8001/mcp
# or
cd mcp && uv run potato-mcp
```

Over stdio, so a client can spawn the process itself:

```bash
just mcp-stdio           # reads MCP_ACCESS_TOKEN / MCP_WORKSPACE_ID
# or
cd mcp && MCP_TRANSPORT=stdio uv run potato-mcp
```

Client config example:

```json
{
  "mcpServers": {
    "sturdy-potato-tasks": {
      "command": "uv",
      "args": ["run", "potato-mcp"],
      "cwd": "/path/to/sturdy-potato/mcp",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "MCP_ACCESS_TOKEN": "<access-jwt>",
        "MCP_WORKSPACE_ID": "1"
      }
    }
  }
}
```

## Tools

`list_tasks`, `get_task`, `create_task`, `update_task`, `delete_task`,
`move_task` — all scoped to the header-resolved user + workspace.
