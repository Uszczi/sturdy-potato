import { create } from "zustand";
import type {
  ProjectSchema,
  TodoSchema,
  TodoCreateInput,
} from "../../api-client";
import { ResponseError } from "../../api-client";
import { logout } from "../services/auth";
import { createProject, listProjects } from "../services/projects";
import {
  assignTaskProject,
  createTask,
  listTasks,
  toggleTask,
} from "../services/tasks";

type AppState = {
  // Domain data, shared by the sidebar and every page.
  projects: ProjectSchema[];
  tasks: TodoSchema[];
  loaded: boolean;
  loading: boolean;
  error: string | null;
  /** Set when the API rejects our token; the shell redirects to login. */
  unauthorized: boolean;

  // Shared UI state.
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Data actions. Each mutation refreshes so `taskCount` stays in sync.
  refresh: () => Promise<void>;
  addProject: (name: string) => Promise<void>;
  addTask: (input: TodoCreateInput) => Promise<void>;
  toggleTask: (task: TodoSchema) => Promise<void>;
  assignTaskProject: (taskId: number, projectId: number | null) => Promise<void>;
};

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

export const useAppStore = create<AppState>((set, get) => ({
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

  addProject: async (name) => {
    const ok = await guard(set, () => createProject(name).then(() => undefined));
    if (ok) await get().refresh();
  },

  addTask: async (input) => {
    const ok = await guard(set, () => createTask(input).then(() => undefined));
    if (ok) await get().refresh();
  },

  toggleTask: async (task) => {
    const ok = await guard(set, () => toggleTask(task).then(() => undefined));
    if (ok) await get().refresh();
  },

  assignTaskProject: async (taskId, projectId) => {
    const ok = await guard(set, () =>
      assignTaskProject(taskId, projectId).then(() => undefined),
    );
    if (ok) await get().refresh();
  },
}));
