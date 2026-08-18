import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { logout } from "../services/auth";
import { useAppStore } from "../stores/app-store";

const inactiveLink =
  "text-base-content/70 hover:bg-base-100 hover:text-base-content";
const activeLink = "bg-primary/10 font-bold text-primary";

/** The persistent app navigation. Mirrors the sidebar in templates/base.html. */
function Sidebar() {
  const navigate = useNavigate();
  const projects = useAppStore((state) => state.projects);
  const open = useAppStore((state) => state.sidebarOpen);
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen);
  const onNavigate = () => setSidebarOpen(false);
  const { pathname, search } = useRouterState({
    select: (state) => state.location,
  });
  const view = (search as { view?: string }).view;
  const onTasks = pathname === "/tasks";
  const activeProjectId = matchProjectId(pathname);

  function handleLogout() {
    logout();
    navigate({ to: "/logged-out" });
  }

  function navClass(isActive: boolean) {
    return `${isActive ? activeLink : inactiveLink} flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-colors`;
  }

  return (
    <aside
      className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-base-300 bg-base-200/70 px-3 py-4 shadow-xl transition-[translate] duration-300 lg:shadow-none"
      style={{ translate: open ? "0 0" : "-100% 0" }}
      aria-label="Primary navigation"
    >
      <div className="flex items-center justify-between">
        <Link
          to="/"
          onClick={onNavigate}
          className="group flex items-center gap-3 rounded-lg px-3 py-2"
        >
          <span className="grid size-9 place-items-center rounded-xl bg-primary text-sm font-black text-primary-content shadow-sm transition-transform group-hover:-rotate-6">
            sp
          </span>
          <span>
            <span className="block text-base font-black tracking-tight">
              sturdy potato
            </span>
          </span>
        </Link>
        <button
          type="button"
          className="btn btn-circle btn-ghost btn-sm lg:hidden"
          onClick={onNavigate}
          aria-label="Close navigation"
        >
          ×
        </button>
      </div>

      <Link
        to="/tasks"
        search={{ compose: true }}
        onClick={onNavigate}
        className="mt-7 flex items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2.5 text-sm font-bold text-primary-content shadow-sm transition hover:bg-primary/90"
      >
        <svg
          aria-hidden="true"
          className="size-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2.5"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14m-7-7h14" />
        </svg>
        Add task
      </Link>

      <div className="mt-5">
        <nav className="space-y-0.5" onClick={onNavigate}>
          <Link
            to="/tasks"
            className={navClass(onTasks && !view)}
          >
            <svg
              aria-hidden="true"
              className="size-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="1.8"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 5h14v14H5z" />
            </svg>
            Inbox
          </Link>
          <Link
            to="/tasks"
            search={{ view: "today" }}
            className={navClass(onTasks && view === "today")}
          >
            <svg
              aria-hidden="true"
              className="size-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="1.8"
            >
              <circle cx="12" cy="12" r="8.5" />
              <path strokeLinecap="round" d="M12 7v5l3 2" />
            </svg>
            Today
          </Link>
          <Link
            to="/tasks"
            search={{ view: "upcoming" }}
            className={navClass(onTasks && view === "upcoming")}
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
                d="M5 19 19 5m0 0H8m11 0v11"
              />
            </svg>
            Upcoming
          </Link>
        </nav>
      </div>

      <div className="mt-8 min-h-0 flex-1">
        <div className="flex items-center justify-between px-3">
          <p className="text-xs font-bold text-base-content/55">Projects</p>
          <Link
            to="/projects"
            search={{ compose: true }}
            onClick={onNavigate}
            className="grid size-6 place-items-center rounded-md text-base-content/55 transition hover:bg-base-100 hover:text-primary"
            aria-label="Manage projects"
          >
            +
          </Link>
        </div>
        <nav
          className="mt-2 max-h-full space-y-0.5 overflow-y-auto"
          onClick={onNavigate}
        >
          {projects.length === 0 ? (
            <Link
              to="/projects"
              className="block rounded-lg px-3 py-2 text-sm text-base-content/50 transition-colors hover:bg-base-100 hover:text-base-content"
            >
              Add your first project
            </Link>
          ) : (
            projects.map((project) => (
              <Link
                key={project.id}
                to="/projects/$projectId"
                params={{ projectId: String(project.id) }}
                className={`${
                  activeProjectId === project.id ? activeLink : inactiveLink
                } flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-semibold transition-colors`}
              >
                <span
                  className="size-2.5 rounded-full bg-primary/70"
                  aria-hidden="true"
                />
                <span className="min-w-0 flex-1 truncate">{project.name}</span>
                <span className="text-xs font-normal text-base-content/40">
                  {project.taskCount ?? 0}
                </span>
              </Link>
            ))
          )}
        </nav>
      </div>

      <div className="mt-4 border-t border-base-300 pt-3">
        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-base-content/70 transition-colors hover:bg-base-100 hover:text-base-content"
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
              d="M15 12H3m0 0 4-4m-4 4 4 4m6-11h5a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-5"
            />
          </svg>
          Log out
        </button>
      </div>
    </aside>
  );
}

/** Pull the numeric id out of a `/projects/<id>` pathname, if present. */
function matchProjectId(pathname: string): number | null {
  const match = pathname.match(/^\/projects\/(\d+)$/);
  return match ? Number(match[1]) : null;
}

export default Sidebar;
