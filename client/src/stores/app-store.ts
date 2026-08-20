import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  ProjectSchema,
  TaskSchema,
  TaskCreateInput,
  TaskUpdateInput,
} from "@api-client";
import { ResponseError } from "@api-client";
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
};

function compareTasks(a: TaskSchema, b: TaskSchema): number {
  const aDone = isTaskDone(a);
  const bDone = isTaskDone(b);
  if (aDone !== bDone) return aDone ? 1 : -1;
  if (!aDone) {
    if (a.position !== b.position) return a.position - b.position;
  } else if (a.updatedAt.getTime() !== b.updatedAt.getTime()) {
    return b.updatedAt.getTime() - a.updatedAt.getTime();
  }
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
    }),
    {
      name: "app-store",
    },
  ),
);
