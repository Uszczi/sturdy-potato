import { api } from "../api";
import type { TodoSchema, TodoCreateInput } from "../../api-client";

/** Every task for the signed-in user, in server order. */
export function listTasks(): Promise<TodoSchema[]> {
  return api.apiTasksList();
}

/** Create a task from composer input (title, optional due date and project). */
export function createTask(input: TodoCreateInput): Promise<TodoSchema> {
  return api.apiTasksCreate({ todoCreateInput: input });
}

/** Flip a task between open and completed. */
export function toggleTask(task: TodoSchema): Promise<TodoSchema> {
  return api.apiTasksPartialUpdate({
    id: String(task.id),
    todoUpdateInput: { completed: !task.completed },
  });
}

/** Move a task to a project, or to the inbox when `projectId` is null. */
export function assignTaskProject(
  taskId: number,
  projectId: number | null,
): Promise<TodoSchema> {
  return api.apiTasksPartialUpdate({
    id: String(taskId),
    todoUpdateInput: { projectId },
  });
}
