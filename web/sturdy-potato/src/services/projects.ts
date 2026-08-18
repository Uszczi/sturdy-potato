import { api } from "../api";
import type { ProjectSchema } from "../../api-client";

/** Every project for the signed-in user, each carrying its `taskCount`. */
export function listProjects(): Promise<ProjectSchema[]> {
  return api.apiProjectsList();
}

/** A single project by id (used by the project detail page). */
export function getProject(id: number): Promise<ProjectSchema> {
  return api.apiProjectsRetrieve({ id: String(id) });
}

/** Create a project and return it. */
export function createProject(name: string): Promise<ProjectSchema> {
  return api.apiProjectsCreate({ projectCreateInput: { name } });
}
