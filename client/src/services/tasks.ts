import { tasksApi } from "../api";
import { getWorkspaceId } from "./chat";
import { TaskStatus } from "../../api-client";
import type {
  TaskSchema,
  TaskCreateInput,
  TaskUpdateInput,
} from "../../api-client";

// Every task route is nested under /api/workspaces/{workspace_id}/, so the
// generated client requires a workspaceId on each call (it throws before
// sending the request otherwise). Resolve the caller's workspace — cached after
// the first lookup — and thread it through.

/** Whether a task sits in the terminal `done` status. */
export function isTaskDone(task: TaskSchema): boolean {
  return task.status === TaskStatus.Done;
}

/**
 * Tasks for one board — a single project, or the inbox (`null`). The server
 * returns these in board order (open column first, then done, each by manual
 * position), which is why boards are fetched per project instead of all at once.
 */
export async function fetchBoardTasks(
  projectId: number | null,
): Promise<TaskSchema[]> {
  const workspaceId = await getWorkspaceId();
  return tasksApi.apiTasksViewList(
    projectId === null
      ? { workspaceId, view: "inbox" }
      : { workspaceId, view: "all", project: projectId },
  );
}

/**
 * Tasks for a cross-project date view (today/upcoming). These span many boards,
 * so they're ordered by due date + recency and are not drag-reorderable.
 */
export async function fetchDateView(
  view: "today" | "upcoming",
): Promise<TaskSchema[]> {
  const workspaceId = await getWorkspaceId();
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return tasksApi.apiTasksViewList({ workspaceId, view, tz });
}

/** A small cross-project "next up" preview of open tasks. */
export async function fetchOpenTasks(limit?: number): Promise<TaskSchema[]> {
  const workspaceId = await getWorkspaceId();
  return tasksApi.apiTasksOpenList({ workspaceId, limit });
}

/** How many of the user's tasks are in `status` (all statuses when omitted). */
export async function countTasks(status?: TaskStatus): Promise<number> {
  const workspaceId = await getWorkspaceId();
  const { count } = await tasksApi.apiTasksCountRetrieve({
    workspaceId,
    status,
  });
  return count;
}

export async function createTask(input: TaskCreateInput): Promise<TaskSchema> {
  const workspaceId = await getWorkspaceId();
  return tasksApi.apiTasksCreate({ workspaceId, taskCreateInput: input });
}

export async function updateTask(
  id: number,
  input: TaskUpdateInput,
): Promise<TaskSchema> {
  const workspaceId = await getWorkspaceId();
  return tasksApi.apiTasksPartialUpdate({
    workspaceId,
    id,
    taskUpdateInput: input,
  });
}

/**
 * Move a task to a status column and an index within it (0 = top). Positions are
 * scoped per board column, so this only ever touches the task's own project.
 */
export async function moveTask(
  id: number,
  status: TaskStatus,
  position: number,
): Promise<void> {
  const workspaceId = await getWorkspaceId();
  return tasksApi.apiTasksMoveCreate({
    workspaceId,
    id,
    taskMoveInput: { status, position },
  });
}
