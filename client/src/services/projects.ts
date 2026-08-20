import { projectsApi } from "../api";
import type { ProjectSchema } from "../../api-client";

export function listProjects(): Promise<ProjectSchema[]> {
  return projectsApi.apiProjectsList();
}

export function getProject(id: number): Promise<ProjectSchema> {
  return projectsApi.apiProjectsRetrieve({ id });
}

export function createProject(
  name: string,
  color?: string | null,
): Promise<ProjectSchema> {
  return projectsApi.apiProjectsCreate({ projectCreateInput: { name, color } });
}

export function reorderProjects(orderedIds: number[]): Promise<void> {
  return projectsApi.apiProjectsReorderCreate({
    reorderInput: { order: orderedIds },
  });
}

export function updateProject(
  id: number,
  changes: { name?: string; color?: string | null },
): Promise<ProjectSchema> {
  return projectsApi.apiProjectsPartialUpdate({
    id,
    projectUpdateInput: changes,
  });
}
