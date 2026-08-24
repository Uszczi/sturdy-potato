import { projectsApi } from "../api";
import type { ProjectSchema } from "../../api-client";

// No workspace is passed: project routes take it from the X-Workspace-Id header
// and default to the caller's personal workspace, which is the only one this
// client works in so far.

export async function listProjects(): Promise<ProjectSchema[]> {
  return projectsApi.apiProjectsList();
}

export async function getProject(id: number): Promise<ProjectSchema> {
  return projectsApi.apiProjectsRetrieve({ id });
}

export async function createProject(
  name: string,
  color?: string | null,
): Promise<ProjectSchema> {
  return projectsApi.apiProjectsCreate({
    projectCreateInput: { name, color },
  });
}

export async function reorderProjects(orderedIds: number[]): Promise<void> {
  return projectsApi.apiProjectsReorderCreate({
    reorderInput: { order: orderedIds },
  });
}

export async function updateProject(
  id: number,
  changes: { name?: string; color?: string | null },
): Promise<ProjectSchema> {
  return projectsApi.apiProjectsPartialUpdate({
    id,
    projectUpdateInput: changes,
  });
}
