import { tasksApi } from "../api";
import type {
  TaskSchema,
  TaskCreateInput,
  TaskUpdateInput,
} from "../../api-client";

// No workspace is passed: task routes take it from the X-Workspace-Id header and
// default to the caller's personal workspace, which is the only one this client
// works in so far.

/**
 * Whether a task sits in a terminal status of its own board.
 *
 * Read straight off the server's flag: the same status key can be terminal on
 * one board and not another, so the key alone can't answer this.
 */
export function isTaskDone(task: TaskSchema): boolean {
  return task.isDone;
}

/**
 * Tasks for one board — a single project, or the inbox (`null`). The server
 * returns these in board order (unfinished columns first, then finished, each by
 * manual position), which is why boards are fetched per project, not all at once.
 */
export async function fetchBoardTasks(
  projectId: number | null,
): Promise<TaskSchema[]> {
  return tasksApi.apiTasksViewList(
    projectId === null
      ? { view: "inbox" }
      : { view: "all", project: projectId },
  );
}

/**
 * Tasks for a cross-project date view (today/upcoming). These span many boards,
 * so they're ordered by due date + recency and are not drag-reorderable.
 */
export async function fetchDateView(
  view: "today" | "upcoming",
): Promise<TaskSchema[]> {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return tasksApi.apiTasksViewList({ view, tz });
}

/** A small cross-project "next up" preview of open tasks. */
export async function fetchOpenTasks(limit?: number): Promise<TaskSchema[]> {
  return tasksApi.apiTasksOpenList({ limit });
}

/**
 * How many of the user's tasks are finished / unfinished (all when omitted).
 *
 * Counts span every board, and boards can disagree on which status keys mean
 * finished, so this filters on done-ness rather than a status name.
 */
export async function countTasks(done?: boolean): Promise<number> {
  const { count } = await tasksApi.apiTasksCountRetrieve({ done });
  return count;
}

export async function createTask(input: TaskCreateInput): Promise<TaskSchema> {
  return tasksApi.apiTasksCreate({ taskCreateInput: input });
}

export async function updateTask(
  id: number,
  input: TaskUpdateInput,
): Promise<TaskSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id,
    taskUpdateInput: input,
  });
}

/**
 * Move a task to a status column and an index within it (0 = top). Positions are
 * scoped per board column, so this only ever touches the task's own project.
 * `status` must be a status key the task's own board offers.
 */
export async function moveTask(
  id: number,
  status: string,
  position: number,
): Promise<void> {
  return tasksApi.apiTasksMoveCreate({
    id,
    taskMoveInput: { status, position },
  });
}
