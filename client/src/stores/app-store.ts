import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  ProjectSchema,
  StatusSchema,
  TaskSchema,
  TaskCreateInput,
  TaskUpdateInput,
  WorkflowInput,
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
  fetchBoardTasks,
  isTaskDone,
  moveTask,
  updateTask,
} from "@/services/tasks";
import { fetchWorkflow, saveWorkflow } from "@/services/workflows";

/** A board is one project's tasks, or the inbox (unassigned) when `null`. */
export function boardKey(projectId: number | null): string {
  return projectId === null ? "inbox" : String(projectId);
}

const EMPTY: TaskSchema[] = [];
const NO_COLUMNS: StatusSchema[] = [];

type AppState = {
  projects: ProjectSchema[];
  // Tasks cached per board, keyed by `boardKey`. Boards are loaded lazily the
  // first time one is opened and refetched individually after a mutation, so we
  // never pull the whole task list at once.
  boards: Record<string, TaskSchema[]>;
  // Each board's ordered statuses, keyed by `boardKey` alongside its tasks.
  // Which columns a board has is per-board data, so it travels with the board.
  workflows: Record<string, StatusSchema[]>;
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
  getWorkflow: (projectId: number | null) => StatusSchema[];
  saveWorkflow: (
    projectId: number | null,
    workflow: WorkflowInput,
  ) => Promise<boolean>;

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
  moveTask: (id: number, status: string, position: number) => Promise<void>;
  markTaskDone: (id: number) => Promise<void>;
  reopenTask: (id: number) => Promise<void>;
};

/** Board order: unfinished cards first, then finished, each by manual position. */
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

      /**
       * Send a card to the first column of its own board matching `pick`.
       *
       * Completing and reopening are the same walk — find the board, find the
       * column that plays the role, drop the card at a slot — because neither
       * "done" nor "todo" is a fixed status any more.
       */
      async function moveToColumn(
        id: number,
        pick: (status: StatusSchema) => boolean,
        slot: number,
      ): Promise<void> {
        const found = locate(id);
        if (!found) return;
        const column = get().getWorkflow(found.projectId).find(pick);
        if (!column) return;
        await get().moveTask(id, column.key, slot);
      }

      // Several actions refetch the same shared state (adding a task or a
      // project both reload the project list; switching boards while a save is
      // in flight reloads a board twice). Responses can land out of order, and
      // the slower, staler one would win — showing a project list without the
      // project just created, or a board without the column just added. Each
      // load claims a ticket and discards its own result if another load for
      // the same key started while it was waiting.
      const loads = new Map<string, number>();

      function claim(key: string): () => boolean {
        const ticket = (loads.get(key) ?? 0) + 1;
        loads.set(key, ticket);
        return () => loads.get(key) === ticket;
      }

      async function storeBoard(projectId: number | null): Promise<void> {
        const key = boardKey(projectId);
        const current = claim(`board:${key}`);
        // The columns and the cards are fetched together: a board can't be
        // rendered from tasks alone now that its statuses are per-board.
        const [tasks, workflow] = await Promise.all([
          fetchBoardTasks(projectId),
          fetchWorkflow(projectId),
        ]);
        if (!current()) return;
        set({
          boards: { ...get().boards, [key]: tasks },
          workflows: { ...get().workflows, [key]: workflow },
        });
      }

      return {
        projects: [],
        boards: {},
        workflows: {},
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
            const current = claim("projects");
            const projects = await listProjects();
            if (!current()) return;
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

        getWorkflow: (projectId) =>
          get().workflows[boardKey(projectId)] ?? NO_COLUMNS,

        saveWorkflow: async (projectId, workflow) => {
          const ok = await guard(set, () =>
            saveWorkflow(projectId, workflow).then(() => undefined),
          );
          // Statuses may have been renamed, dropped or merged, so the board's
          // cards can have moved: reload both halves.
          if (ok) await get().refreshBoard(projectId);
          return ok;
        },

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
          const byId = new Map(
            previous.map((project) => [project.id, project]),
          );
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
          // The server never writes a status without its done-ness, so neither
          // does the optimistic copy: sorting and the completion tick both read
          // isDone, and a card dropped in a terminal column would otherwise
          // render as still-open until the refetch landed.
          const landing = get()
            .getWorkflow(projectId)
            .find((candidate) => candidate.key === status);
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
                    ...(task.id === id
                      ? { status, isDone: landing?.isTerminal ?? task.isDone }
                      : null),
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

        markTaskDone: async (id) =>
          // Completing floats the card to the top of its board's first
          // finished column.
          moveToColumn(id, (status) => status.isTerminal, 0),

        reopenTask: async (id) =>
          // The mirror: unfinished work returns to the end of the column its
          // board starts in.
          moveToColumn(
            id,
            (status) => status.isInitial,
            Number.MAX_SAFE_INTEGER,
          ),
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
