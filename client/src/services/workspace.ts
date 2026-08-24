import { workspacesApi } from "../api";

/**
 * The id of the workspace the client works in.
 *
 * Resource routes (tasks, projects, comments, chat) resolve the workspace
 * themselves from the `X-Workspace-Id` header and default to the caller's
 * personal one, so they never need this. The workspace's own routes still name
 * it in the path, which is what this is for. Until the client lets you switch
 * workspaces, that is the first one listed — the personal workspace, which the
 * server sorts to the top. Cached so we resolve it once per session.
 */
let workspaceIdCache: number | null = null;

export async function getWorkspaceId(): Promise<number> {
  if (workspaceIdCache !== null) return workspaceIdCache;
  const workspaces = await workspacesApi.apiWorkspacesList();
  if (workspaces.length === 0) throw new Error("No workspace available.");
  workspaceIdCache = workspaces[0].id;
  return workspaceIdCache;
}
