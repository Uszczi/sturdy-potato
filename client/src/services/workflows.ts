import { projectsApi, workspacesApi } from "../api";
import { getWorkspaceId } from "./chat";
import type { StatusSchema, WorkflowInput } from "../../api-client";

/**
 * A board's workflow: the ordered statuses it renders as columns.
 *
 * Which statuses exist is per-board, so the client can't hard-code them. A
 * project board reads its own; the inbox (`projectId === null`) reads the
 * workspace's, which is also the template every new project is copied from.
 */
export async function fetchWorkflow(
  projectId: number | null,
): Promise<StatusSchema[]> {
  const workspaceId = await getWorkspaceId();
  if (projectId === null) {
    const workspace = await workspacesApi.apiWorkspacesRetrieve({
      workspaceId,
    });
    return workspace.workflow;
  }
  const project = await projectsApi.apiProjectsRetrieve({
    workspaceId,
    id: projectId,
  });
  return project.workflow;
}

/**
 * Replace a board's whole workflow at once.
 *
 * Adding, renaming, reordering and removing all travel in one request: the
 * server validates the finished list (exactly one initial status, at least one
 * terminal) rather than each intermediate step. Any status dropped needs an
 * entry in `reassign` naming where its tasks go.
 */
export async function saveWorkflow(
  projectId: number | null,
  workflowInput: WorkflowInput,
): Promise<StatusSchema[]> {
  const workspaceId = await getWorkspaceId();
  if (projectId === null) {
    const workspace = await workspacesApi.apiWorkspacesStatusesUpdate({
      workspaceId,
      workflowInput,
    });
    return workspace.workflow;
  }
  const project = await projectsApi.apiProjectsStatusesUpdate({
    workspaceId,
    id: projectId,
    workflowInput,
  });
  return project.workflow;
}
