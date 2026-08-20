import { tasksApi } from "../api";
import type { TaskSchema, TaskCreateInput } from "../../api-client";

export function listTasks(): Promise<TaskSchema[]> {
  return tasksApi.apiTasksList();
}

export function createTask(input: TaskCreateInput): Promise<TaskSchema> {
  return tasksApi.apiTasksCreate({ taskCreateInput: input });
}

export function toggleTask(task: TaskSchema): Promise<TaskSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id: task.id,
    taskUpdateInput: { completed: !task.completed },
  });
}

export function reorderTasks(orderedIds: number[]): Promise<void> {
  return tasksApi.apiTasksReorderCreate({ reorderInput: { order: orderedIds } });
}

export function assignTaskProject(
  taskId: number,
  projectId: number | null,
): Promise<TaskSchema> {
  return tasksApi.apiTasksPartialUpdate({
    id: taskId,
    taskUpdateInput: { projectId },
  });
}
