import { projectsApi } from "../api";
import { getWorkspaceId } from "./chat";
import type { ProjectSchema } from "../../api-client";

// Every project route is nested under /api/workspaces/{workspace_id}/, so the
// generated client requires a workspaceId on each call (it throws before
// sending the request otherwise). Resolve the caller's workspace — cached after
// the first lookup — and thread it through.

export async function listProjects(): Promise<ProjectSchema[]> {
  const workspaceId = await getWorkspaceId();
  return projectsApi.apiProjectsList({ workspaceId });
}

export async function getProject(id: number): Promise<ProjectSchema> {
  const workspaceId = await getWorkspaceId();
  return projectsApi.apiProjectsRetrieve({ workspaceId, id });
}

export async function createProject(
  name: string,
  color?: string | null,
): Promise<ProjectSchema> {
  const workspaceId = await getWorkspaceId();
  return projectsApi.apiProjectsCreate({
    workspaceId,
    projectCreateInput: { name, color },
  });
}

export async function reorderProjects(orderedIds: number[]): Promise<void> {
  const workspaceId = await getWorkspaceId();
  return projectsApi.apiProjectsReorderCreate({
    workspaceId,
    reorderInput: { order: orderedIds },
  });
}

export async function updateProject(
  id: number,
  changes: { name?: string; color?: string | null },
): Promise<ProjectSchema> {
  const workspaceId = await getWorkspaceId();
  return projectsApi.apiProjectsPartialUpdate({
    workspaceId,
    id,
    projectUpdateInput: changes,
  });
}
