"""Entrypoint: serve the task tools over stdio or streamable HTTP.

``MCP_TRANSPORT`` selects the transport (default ``http``):

- ``http`` — reachable at ``http://<host>:<port>/mcp``; host/port come from the
  environment so the SPA chat backend can point at it without code changes.
- ``stdio`` — spoken over stdin/stdout so a client can launch this process
  directly (no port, no URL). Credentials come from ``MCP_ACCESS_TOKEN`` and
  ``MCP_WORKSPACE_ID`` instead of request headers (see :mod:`potato_mcp.context`).
"""

import os

from potato_mcp.server import mcp

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8001


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "http")
    if transport == "stdio":
        mcp.run(transport="stdio")
        return
    mcp.run(
        transport="http",
        host=os.getenv("MCP_HOST", DEFAULT_HOST),
        port=int(os.getenv("MCP_PORT", DEFAULT_PORT)),
    )


if __name__ == "__main__":
    main()
