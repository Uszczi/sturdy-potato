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
export function createProject(name: string): Promise<ProjectSchema> {
  return projectsApi.apiProjectsCreate({ projectCreateInput: { name } });
}
