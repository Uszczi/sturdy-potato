import { tasksApi } from "../api";
import { TaskStatus } from "../../api-client";
import type {
  TaskSchema,
  TaskCreateInput,
  TaskUpdateInput,
} from "../../api-client";

/** Whether a task sits in the terminal `done` status. */
export function isTaskDone(task: TaskSchema): boolean {
  return task.status === TaskStatus.Done;
}

/**
 * Tasks for one board — a single project, or the inbox (`null`). The server
 * returns these in board order (open column first, then done, each by manual
 * position), which is why boards are fetched per project instead of all at once.
 */
export function fetchBoardTasks(
  projectId: number | null,
): Promise<TaskSchema[]> {
  return tasksApi.apiTasksViewList(
    projectId === null ? { view: "inbox" } : { view: "all", project: projectId },
  );
}

/**
 * Tasks for a cross-project date view (today/upcoming). These span many boards,
 * so they're ordered by due date + recency and are not drag-reorderable.
 */
export function fetchDateView(view: "today" | "upcoming"): Promise<TaskSchema[]> {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return tasksApi.apiTasksViewList({ view, tz });
}

/** A small cross-project "next up" preview of open tasks. */
export function fetchOpenTasks(limit?: number): Promise<TaskSchema[]> {
  return tasksApi.apiTasksOpenList({ limit });
}

/** How many of the user's tasks are in `status` (all statuses when omitted). */
export async function countTasks(status?: TaskStatus): Promise<number> {
  const { count } = await tasksApi.apiTasksCountRetrieve({ status });
  return count;
}

export function createTask(input: TaskCreateInput): Promise<TaskSchema> {
  return tasksApi.apiTasksCreate({ taskCreateInput: input });
}

export function updateTask(
  id: number,
  input: TaskUpdateInput,
): Promise<TaskSchema> {
  return tasksApi.apiTasksPartialUpdate({ id, taskUpdateInput: input });
}

/**
 * Move a task to a status column and an index within it (0 = top). Positions are
 * scoped per board column, so this only ever touches the task's own project.
 */
export function moveTask(
  id: number,
  status: TaskStatus,
  position: number,
): Promise<void> {
  return tasksApi.apiTasksMoveCreate({
    id,
    taskMoveInput: { status, position },
  });
}
