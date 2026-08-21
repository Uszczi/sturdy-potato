import { Link } from "@tanstack/react-router";

import { useAppStore } from "@/stores/app-store";
import ProjectSelector from "./ProjectSelector";

/** Board controls occupy the shared app sidebar while Kanban is open. */
export function KanbanSidebar() {
  const open = useAppStore((state) => state.sidebarOpen);
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen);

  return (
    <aside
      className="border-base-300 bg-base-200/70 fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r px-3 py-4 shadow-xl transition-[translate] duration-300 lg:shadow-none"
      style={{ translate: open ? "0 0" : "-100% 0" }}
      aria-label="Kanban controls"
    >
      <div className="flex shrink-0 items-center justify-between px-3 py-2">
        <Link
          to="/"
          onClick={() => setSidebarOpen(false)}
          className="group flex items-center gap-3 rounded-lg"
        >
          <span className="bg-primary text-primary-content grid size-9 place-items-center rounded-xl text-sm font-black shadow-sm transition-transform group-hover:-rotate-6">
            sp
          </span>
          <span className="text-base font-black tracking-tight">Kanban</span>
        </Link>
        <button
          type="button"
          className="btn btn-circle btn-ghost btn-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close Kanban controls"
        >
          ×
        </button>
      </div>

      <div className="border-base-300 mt-6 border-y px-3 py-5">
        <p className="text-base-content/55 text-xs font-bold tracking-[0.14em] uppercase">
          Board project
        </p>
        <div className="mt-3">
          <ProjectSelector />
        </div>
      </div>

      <div className="mt-4 px-1">
        <Link
          to="/tasks"
          onClick={() => setSidebarOpen(false)}
          className="text-base-content/70 hover:bg-base-100 hover:text-base-content flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-colors"
        >
          <svg
            aria-hidden="true"
            className="size-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="1.8"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="m15 18-6-6 6-6"
            />
          </svg>
          Back to tasks
        </Link>
      </div>
    </aside>
  );
}
