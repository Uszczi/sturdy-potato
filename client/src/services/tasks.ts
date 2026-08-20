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

export function listTasks(): Promise<TaskSchema[]> {
  return tasksApi.apiTasksList();
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

export function reorderTasks(orderedIds: number[]): Promise<void> {
  return tasksApi.apiTasksReorderCreate({
    reorderInput: { order: orderedIds },
  });
}
