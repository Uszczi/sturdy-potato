import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  ProjectSchema,
  TaskSchema,
  TaskCreateInput,
  TaskUpdateInput,
} from "@api-client";
import { ResponseError, TaskStatus } from "@api-client";
import { logout } from "@/services/auth";
import {
  createProject,
  listProjects,
  reorderProjects,
  updateProject,
} from "@/services/projects";
import {
  createTask,
  isTaskDone,
  listTasks,
  reorderTasks,
  updateTask,
} from "@/services/tasks";

type AppState = {
  projects: ProjectSchema[];
  tasks: TaskSchema[];
  loaded: boolean;
  loading: boolean;
  error: string | null;
  unauthorized: boolean;

  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  kanbanSelectedProject: ProjectSchema | null;
  setKanbanSelectedProject: (project: ProjectSchema | null) => void;

  getTasksForProject: (projectId: number | null) => TaskSchema[];

  refresh: () => Promise<void>;
  addProject: (name: string, color?: string | null) => Promise<void>;
  updateProject: (
    id: number,
    changes: { name?: string; color?: string | null },
  ) => Promise<void>;
  reorderProjects: (orderedIds: number[]) => Promise<void>;
  addTask: (input: TaskCreateInput) => Promise<void>;
  updateTask: (id: number, input: TaskUpdateInput) => Promise<void>;
  assignTaskProject: (
    taskId: number,
    projectId: number | null,
  ) => Promise<void>;
  reorderTasks: (orderedIds: number[]) => Promise<void>;
  moveTask: (
    id: number,
    status: TaskStatus,
    orderedIds: number[],
  ) => Promise<void>;
  markTaskDone: (id: number) => Promise<void>;
};

function compareTasks(a: TaskSchema, b: TaskSchema): number {
  const aDone = isTaskDone(a);
  const bDone = isTaskDone(b);
  if (aDone !== bDone) return aDone ? 1 : -1;
  // Open first, then done; within each group tasks keep their manual position
  // so both kanban columns can be reordered by drag-and-drop.
  if (a.position !== b.position) return a.position - b.position;
  if (a.createdAt.getTime() !== b.createdAt.getTime()) {
    return b.createdAt.getTime() - a.createdAt.getTime();
  }
  return b.id - a.id;
}

/**
 * Wrap an API call so an expired-token 401 flips the store into an
 * `unauthorized` state (the app shell watches this and redirects to login)
 * while other errors surface as a message. Returns whether the call succeeded.
 */
async function guard(
  set: (partial: Partial<AppState>) => void,
  run: () => Promise<void>,
): Promise<boolean> {
  try {
    await run();
    return true;
  } catch (error) {
    if (error instanceof ResponseError && error.response.status === 401) {
      logout();
      set({ unauthorized: true });
    } else {
      set({ error: "Something went wrong. Please try again." });
    }
    return false;
  }
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      projects: [],
      tasks: [],
      loaded: false,
      loading: false,
      error: null,
      unauthorized: false,

      sidebarOpen:
        typeof window === "undefined" ? true : window.innerWidth >= 1024,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),

      kanbanSelectedProject: null,
      setKanbanSelectedProject: (project) =>
        set({ kanbanSelectedProject: project }),

      getTasksForProject: (projectId) =>
        get().tasks.filter((task) => task.projectId === projectId),

      refresh: async () => {
        set({ loading: true, error: null });
        await guard(set, async () => {
          const [projects, tasks] = await Promise.all([
            listProjects(),
            listTasks(),
          ]);
          set({ projects, tasks, loaded: true });
        });
        set({ loading: false });
      },

      addProject: async (name, color) => {
        const ok = await guard(set, () =>
          createProject(name, color).then(() => undefined),
        );
        if (ok) await get().refresh();
      },

      updateProject: async (id, changes) => {
        // Only name/color change here, never task counts, so patch the affected
        // project in place instead of refetching the whole workspace.
        await guard(set, async () => {
          const updated = await updateProject(id, changes);
          const projects = get().projects.map((existing) =>
            existing.id === updated.id ? updated : existing,
          );
          set({ projects });
        });
      },

      reorderProjects: async (orderedIds) => {
        const previous = get().projects;
        const byId = new Map(previous.map((project) => [project.id, project]));
        const optimistic = orderedIds
          .map((id) => byId.get(id))
          .filter((project): project is ProjectSchema => project !== undefined);
        // Optimistically apply the new order, then persist and roll back on failure.
        set({ projects: optimistic });
        const ok = await guard(set, () => reorderProjects(orderedIds));
        if (!ok) set({ projects: previous });
      },

      addTask: async (input) => {
        const ok = await guard(set, () =>
          createTask(input).then(() => undefined),
        );
        if (ok) await get().refresh();
      },

      updateTask: async (id, input) => {
        // Field edits like status never change project task counts, so patch the
        // affected task in place and re-sort instead of refetching everything.
        await guard(set, async () => {
          const updated = await updateTask(id, input);
          const tasks = get()
            .tasks.map((existing) =>
              existing.id === updated.id ? updated : existing,
            )
            .sort(compareTasks);
          set({ tasks });
        });
      },

      assignTaskProject: async (taskId, projectId) => {
        // Reassigning a project shifts task counts on both projects, so refetch the
        // workspace rather than patching a single task in place.
        const ok = await guard(set, () =>
          updateTask(taskId, { projectId }).then(() => undefined),
        );
        if (ok) await get().refresh();
      },

      reorderTasks: async (orderedIds) => {
        const previous = get().tasks;
        // Mirror the server: only the slots the moved tasks occupy get new
        // positions, so gather those positions and hand them out in the new order.
        const moved = new Set(orderedIds);
        const slots = previous
          .filter((task) => moved.has(task.id))
          .map((task) => task.position)
          .sort((a, b) => a - b);
        const nextPosition = new Map(
          orderedIds.map((id, index) => [id, slots[index]]),
        );
        const optimistic = previous
          .map((task) =>
            nextPosition.has(task.id)
              ? { ...task, position: nextPosition.get(task.id)! }
              : task,
          )
          .sort(compareTasks);
        // Optimistically apply so the row lands immediately, then persist.
        set({ tasks: optimistic });
        const ok = await guard(set, () => reorderTasks(orderedIds));
        // Roll back if the server rejected the new order.
        if (!ok) set({ tasks: previous });
      },

      moveTask: async (id, status, orderedIds) => {
        const previous = get().tasks;
        // Redistribute the destination column's position slots in the requested
        // order (same slot-borrowing rule as reorderTasks) while flipping the
        // moved task's status, so the card holds the slot it was dropped into
        // instead of snapping to a default spot after the round-trip.
        const moved = new Set(orderedIds);
        const slots = previous
          .filter((task) => moved.has(task.id))
          .map((task) => task.position)
          .sort((a, b) => a - b);
        const nextPosition = new Map(
          orderedIds.map((taskId, index) => [taskId, slots[index]]),
        );
        const optimistic = previous
          .map((task) => {
            if (task.id !== id && !nextPosition.has(task.id)) return task;
            return {
              ...task,
              ...(task.id === id ? { status } : null),
              ...(nextPosition.has(task.id)
                ? { position: nextPosition.get(task.id)! }
                : null),
            };
          })
          .sort(compareTasks);
        // Apply both changes in one update so the board doesn't flicker between
        // the status change landing and the reorder landing.
        set({ tasks: optimistic });
        // Persist status first so the task belongs to the destination column,
        // then its order; roll the whole move back if either leg fails.
        const ok = await guard(set, async () => {
          await updateTask(id, { status });
          await reorderTasks(orderedIds);
        });
        if (!ok) set({ tasks: previous });
      },

      markTaskDone: async (id) => {
        // Completing a task moves it to the (position-ordered) done group; float
        // it to the top so the list keeps the just-ticked item on top, matching
        // the recency feel the list views had before done became sortable.
        const doneIds = [
          id,
          ...get()
            .tasks.filter((task) => isTaskDone(task) && task.id !== id)
            .map((task) => task.id),
        ];
        await get().moveTask(id, TaskStatus.Done, doneIds);
      },
    }),
    {
      name: "app-store",
    },
  ),
);
