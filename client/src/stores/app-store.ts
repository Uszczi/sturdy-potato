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
  fetchBoardTasks,
  isTaskDone,
  moveTask,
  updateTask,
} from "@/services/tasks";

/** A board is one project's tasks, or the inbox (unassigned) when `null`. */
export function boardKey(projectId: number | null): string {
  return projectId === null ? "inbox" : String(projectId);
}

const EMPTY: TaskSchema[] = [];

type AppState = {
  projects: ProjectSchema[];
  // Tasks cached per board, keyed by `boardKey`. Boards are loaded lazily the
  // first time one is opened and refetched individually after a mutation, so we
  // never pull the whole task list at once.
  boards: Record<string, TaskSchema[]>;
  loaded: boolean;
  loading: boolean;
  error: string | null;
  unauthorized: boolean;

  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  kanbanSelectedProject: ProjectSchema | null;
  setKanbanSelectedProject: (project: ProjectSchema | null) => void;

  loadProjects: () => Promise<void>;
  ensureBoard: (projectId: number | null) => Promise<void>;
  refreshBoard: (projectId: number | null) => Promise<void>;
  getBoard: (projectId: number | null) => TaskSchema[];

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
  moveTask: (
    id: number,
    status: TaskStatus,
    position: number,
  ) => Promise<void>;
  markTaskDone: (id: number) => Promise<void>;
};

/** Board order: open column first, then done, each by manual position. */
function compareTasks(a: TaskSchema, b: TaskSchema): number {
  const aDone = isTaskDone(a);
  const bDone = isTaskDone(b);
  if (aDone !== bDone) return aDone ? 1 : -1;
  if (a.position !== b.position) return a.position - b.position;
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
    (set, get) => {
      /** Find a cached task and the board (project) it lives in. */
      function locate(
        id: number,
      ): { task: TaskSchema; projectId: number | null } | null {
        for (const tasks of Object.values(get().boards)) {
          const task = tasks.find((candidate) => candidate.id === id);
          if (task) return { task, projectId: task.projectId };
        }
        return null;
      }

      async function storeBoard(projectId: number | null): Promise<void> {
        const tasks = await fetchBoardTasks(projectId);
        set({
          boards: { ...get().boards, [boardKey(projectId)]: tasks },
        });
      }

      return {
        projects: [],
        boards: {},
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

        loadProjects: async () => {
          set({ loading: true, error: null });
          await guard(set, async () => {
            const projects = await listProjects();
            set({ projects, loaded: true });
          });
          set({ loading: false });
        },

        ensureBoard: async (projectId) => {
          if (boardKey(projectId) in get().boards) return;
          await guard(set, () => storeBoard(projectId));
        },

        refreshBoard: async (projectId) => {
          await guard(set, () => storeBoard(projectId));
        },

        getBoard: (projectId) => get().boards[boardKey(projectId)] ?? EMPTY,

        addProject: async (name, color) => {
          const ok = await guard(set, () =>
            createProject(name, color).then(() => undefined),
          );
          if (ok) await get().loadProjects();
        },

        updateProject: async (id, changes) => {
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
            .filter(
              (project): project is ProjectSchema => project !== undefined,
            );
          set({ projects: optimistic });
          const ok = await guard(set, () => reorderProjects(orderedIds));
          if (!ok) set({ projects: previous });
        },

        addTask: async (input) => {
          const ok = await guard(set, () =>
            createTask(input).then(() => undefined),
          );
          if (!ok) return;
          // Refetch only the board it landed on; reload projects for task counts.
          await get().refreshBoard(input.projectId ?? null);
          await get().loadProjects();
        },

        updateTask: async (id, input) => {
          const found = locate(id);
          const ok = await guard(set, () =>
            updateTask(id, input).then(() => undefined),
          );
          if (!ok) return;
          // A field or status edit stays on the same board; refetch just that
          // one (fall back to the task's project when we know it).
          await get().refreshBoard(found?.projectId ?? null);
        },

        assignTaskProject: async (taskId, projectId) => {
          const found = locate(taskId);
          const ok = await guard(set, () =>
            updateTask(taskId, { projectId }).then(() => undefined),
          );
          if (!ok) return;
          // Reassigning moves the task between two boards, so refresh both and
          // the project counts.
          if (found) await get().refreshBoard(found.projectId);
          await get().refreshBoard(projectId);
          await get().loadProjects();
        },

        moveTask: async (id, status, position) => {
          const found = locate(id);
          if (!found) return;
          const projectId = found.projectId;
          const key = boardKey(projectId);
          const previous = get().boards[key] ?? EMPTY;
          // Mirror the server so the card holds its slot without a flicker:
          // rebuild the destination column with the card at `position`, then
          // renumber that column 0..N while flipping the moved card's status.
          const column = previous
            .filter((task) => task.status === status && task.id !== id)
            .sort(compareTasks)
            .map((task) => task.id);
          column.splice(Math.min(position, column.length), 0, id);
          const rank = new Map(column.map((taskId, index) => [taskId, index]));
          const optimistic = previous
            .map((task) =>
              rank.has(task.id)
                ? {
                    ...task,
                    ...(task.id === id ? { status } : null),
                    position: rank.get(task.id)!,
                  }
                : task,
            )
            .sort(compareTasks);
          set({ boards: { ...get().boards, [key]: optimistic } });
          const ok = await guard(set, () => moveTask(id, status, position));
          // Reconcile with the server's numbering, or roll back on failure.
          if (ok) await get().refreshBoard(projectId);
          else set({ boards: { ...get().boards, [key]: previous } });
        },

        markTaskDone: async (id) => {
          // Completing floats the card to the top of its board's done column.
          await get().moveTask(id, TaskStatus.Done, 0);
        },
      };
    },
    {
      name: "app-store",
      // Only persist UI preferences; task/project data is refetched on load so
      // it never goes stale (and Date fields don't survive JSON round-trips).
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        kanbanSelectedProject: state.kanbanSelectedProject,
      }),
    },
  ),
);
