import { projectsApi } from "../api";
import type { ProjectSchema } from "../../api-client";

/** Every project for the signed-in user, each carrying its `taskCount`. */
export function listProjects(): Promise<ProjectSchema[]> {
  return projectsApi.apiProjectsList();
}

/** A single project by id (used by the project detail page). */
export function getProject(id: number): Promise<ProjectSchema> {
  return projectsApi.apiProjectsRetrieve({ id });
}

/** Create a project and return it. */
export function createProject(
  name: string,
  color?: string | null,
): Promise<ProjectSchema> {
  return projectsApi.apiProjectsCreate({ projectCreateInput: { name, color } });
}

/** Persist a drag-and-drop reorder of the project list (their new order). */
export function reorderProjects(orderedIds: number[]): Promise<void> {
  return projectsApi.apiProjectsReorderCreate({
    reorderInput: { order: orderedIds },
  });
}

/** Patch a project's mutable fields (name, color) and return the fresh row. */
export function updateProject(
  id: number,
  changes: { name?: string; color?: string | null },
): Promise<ProjectSchema> {
  return projectsApi.apiProjectsPartialUpdate({
    id,
    projectUpdateInput: changes,
  });
}
