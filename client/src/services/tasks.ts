import { tasksApi } from "../api";
import type { TaskSchema, TaskCreateInput } from "../../api-client";

/** Every task for the signed-in user, in server order. */
export function listTasks(): Promise<TaskSchema[]> {
  return tasksApi.apiTasksList();
}

/** Create a task from composer input (title, optional due date and project). */
export function createTask(input: TaskCreateInput): Promise<TaskSchema> {
  return tasksApi.apiTasksCreate({ taskCreateInput: input });
}

/** Flip a task between open and completed. */
export function toggleTask(task: TaskSchema): Promise<TaskSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id: task.id,
    taskUpdateInput: { completed: !task.completed },
  });
}

/**
 * Persist a manual ordering. `orderedIds` is the new order of the moved tasks;
 * the server reassigns their positions to the slots those tasks occupy.
 */
export function reorderTasks(orderedIds: number[]): Promise<void> {
  return tasksApi.apiTasksReorderCreate({ reorderInput: { order: orderedIds } });
}

/** Move a task to a project, or to the inbox when `projectId` is null. */
export function assignTaskProject(
  taskId: number,
  projectId: number | null,
): Promise<TaskSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id: taskId,
    taskUpdateInput: { projectId },
  });
}
