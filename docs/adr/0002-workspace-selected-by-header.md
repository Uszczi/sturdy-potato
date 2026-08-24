# The Workspace a request acts on travels in a header

Every Task, Project and Comment belongs to a Workspace, so every resource route
needs to know which one. Nesting them under `/api/workspaces/{workspace_id}/...`
put that choice in the URL, which meant no caller could address a Task without
first discovering a Workspace id: the SPA opened its session by listing
Workspaces, caching the first one, and threading it through every generated
client call, and the MCP server — which reads `X-Workspace-Id` — already
disagreed with the API about where the answer comes from.

The Workspace is ambient context, not part of a resource's identity: `/api/tasks/`
names the same Task no matter which Workspace the caller is looking through.
Resource routes therefore take it from the `X-Workspace-Id` request header, and a
request that sends no header acts on the caller's Personal Workspace. Membership
is authorized the same way either way, and a Workspace the caller does not belong
to 404s rather than 403s, so the header cannot be used to probe which Workspaces
exist.

The Workspace's own routes keep the id in the path (`/api/workspaces/{id}/`,
`/api/workspaces/{id}/statuses/`): there the id *is* the resource being addressed.

## Considered Options

**Keep the id in the path.** Every URL is self-describing and cacheable per
workspace. But it forces a workspace lookup on every client before its first
request, duplicates the id into paths that already carry a task or project id,
and leaves the REST API and the MCP server carrying the same value two different
ways.

**A query parameter (`?workspace=`).** Same ambient-context reading, and visible
in a browser address bar — which is also the problem: it invites the id into
bookmarks and logs as though it were part of the resource, and it collides with
the filters (`view`, `project`, `done`) that genuinely select *within* a
workspace.

**Bind the workspace to the session, in the access token.** Removes the choice
from the request entirely, but switching workspaces would then mean re-issuing a
token, and one client could no longer hold two boards from different workspaces
open at once.

## Consequences

Requests are no longer self-describing: a URL alone does not say which Workspace
it read, so anything replaying or logging a request must carry the header with
it. In exchange a single-Workspace client — which is what the SPA is today — does
no workspace resolution at all, and the REST API, the MCP server and the chat
route all name the Workspace the same way.

The fallback makes "the caller has no Personal Workspace" a reachable state.
Registration mints exactly one per User, so it only arises if that Workspace is
deleted out from under them; such a request 404s rather than silently picking
some other Workspace the caller happens to belong to.

Membership is checked on every request either way, so the header is a selector,
not a grant: naming another Workspace's id gets a 404 exactly as the old path
segment did.
