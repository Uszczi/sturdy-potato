import { tasksApi } from "../api";
import type { TodoSchema, TodoCreateInput } from "../../api-client";

/** Every task for the signed-in user, in server order. */
export function listTasks(): Promise<TodoSchema[]> {
  return tasksApi.apiTasksList();
}

/** Create a task from composer input (title, optional due date and project). */
export function createTask(input: TodoCreateInput): Promise<TodoSchema> {
  return tasksApi.apiTasksCreate({ todoCreateInput: input });
}

/** Flip a task between open and completed. */
export function toggleTask(task: TodoSchema): Promise<TodoSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id: task.id,
    todoUpdateInput: { completed: !task.completed },
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
): Promise<TodoSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id: taskId,
    todoUpdateInput: { projectId },
  });
}
