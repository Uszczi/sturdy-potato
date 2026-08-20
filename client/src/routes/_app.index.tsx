import { Link, createFileRoute } from "@tanstack/react-router";
import MenuButton from "../components/MenuButton";
import { getUsername } from "../services/auth";
import { formatToday } from "../services/format";
import { isTaskDone } from "../services/tasks";
import { useAppStore } from "../stores/app-store";

export const Route = createFileRoute("/_app/")({
  component: Overview,
});

/** Short "Aug 17" label for a timestamp, in local time. */
function shortDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(date);
}

function Overview() {
  const projects = useAppStore((state) => state.projects);
  const tasks = useAppStore((state) => state.tasks);

  const openTasks = tasks.filter((task) => !isTaskDone(task));
  const completedCount = tasks.length - openTasks.length;
  const username = getUsername();
  const projectName = (id: number | null) =>
    projects.find((project) => project.id === id)?.name ?? "No project";

  return (
    <div className="container mx-auto min-h-screen max-w-5xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <header className="border-base-300 flex flex-col gap-5 border-b pb-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <MenuButton />
          <div>
            <p className="text-base-content/45 text-xs font-bold tracking-[0.18em] uppercase">
              {formatToday(new Date())}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 sm:pt-1">
          <span className="hidden text-right sm:block">
            <span className="block text-sm font-bold">{username}</span>
            <span className="text-base-content/50 block text-xs">
              Personal workspace
            </span>
          </span>
          <span className="bg-primary text-primary-content grid size-9 place-items-center rounded-full text-sm font-bold">
            {username.charAt(0).toUpperCase()}
          </span>
        </div>
      </header>

      <div className="mt-5 flex flex-wrap gap-2">
        <Link
          to="/tasks"
          search={{ compose: true }}
          className="btn btn-primary btn-sm gap-2"
        >
          <svg
            aria-hidden="true"
            className="size-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <path strokeLinecap="round" d="M12 5v14m-7-7h14" />
          </svg>
          Add task
        </Link>
        <Link
          to="/projects"
          className="btn btn-ghost text-base-content/65 btn-sm hover:bg-base-200 hover:text-base-content"
        >
          Browse projects
        </Link>
      </div>

      <section
        className="border-base-300 mt-8 grid border-y sm:grid-cols-3"
        aria-label="Workspace summary"
      >
        <SummaryCard label="Open tasks" value={openTasks.length} bordered />
        <SummaryCard label="Completed" value={completedCount} bordered />
        <SummaryCard label="Projects" value={projects.length} />
      </section>

      <section className="mt-10 grid gap-10 xl:grid-cols-[1.25fr_1fr]">
        <article>
          <header className="flex items-end justify-between gap-4">
            <div>
              <p className="text-primary text-xs font-bold tracking-[0.16em] uppercase">
                Next up
              </p>
              <h2 className="mt-1 text-xl font-bold tracking-tight">
                Open tasks
              </h2>
            </div>
            <Link
              to="/tasks"
              className="text-primary text-sm font-semibold hover:underline"
            >
              See all
            </Link>
          </header>
          {openTasks.length > 0 ? (
            <ul className="divide-base-300 border-base-300 mt-4 divide-y border-y">
              {openTasks.slice(0, 6).map((task) => (
                <li key={task.id} className="flex items-center gap-3 py-3.5">
                  <span className="border-primary size-4 shrink-0 rounded-full border-2" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold">
                      {task.title}
                    </p>
                    <p className="text-base-content/50 mt-0.5 truncate text-xs">
                      {projectName(task.projectId)}
                    </p>
                  </div>
                  <span className="text-base-content/40 text-xs">
                    {task.createdAt.toString().slice(0, 10)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="border-base-300 text-base-content/55 mt-4 border-y px-1 py-6 text-sm">
              Your inbox is clear. Enjoy the quiet.
            </p>
          )}
        </article>

        <article>
          <header className="flex items-end justify-between gap-4">
            <div>
              <p className="text-primary text-xs font-bold tracking-[0.16em] uppercase">
                Structure
              </p>
              <h2 className="mt-1 text-xl font-bold tracking-tight">
                Projects
              </h2>
            </div>
            <Link
              to="/projects"
              className="text-primary text-sm font-semibold hover:underline"
            >
              Manage
            </Link>
          </header>
          {projects.length > 0 ? (
            <ul className="divide-base-300 border-base-300 mt-4 divide-y border-y">
              {projects.slice(0, 4).map((project) => (
                <li key={project.id}>
                  <Link
                    to="/projects/$projectId"
                    params={{ projectId: String(project.id) }}
                    className="hover:text-primary flex items-center gap-3 py-3.5 transition-colors"
                  >
                    <span
                      className="bg-primary/75 size-2.5 shrink-0 rounded-full"
                      aria-hidden="true"
                    />
                    <span className="min-w-0 flex-1 truncate text-sm font-semibold">
                      {project.name}
                    </span>
                    <span className="text-base-content/45 text-xs">
                      {project.taskCount ?? 0}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <div className="border-base-300 mt-4 border-y px-1 py-6">
              <p className="text-base-content/55 text-sm">
                Projects give your tasks a home.
              </p>
              <Link
                to="/projects"
                search={{ compose: true }}
                className="text-primary mt-3 inline-block text-sm font-semibold hover:underline"
              >
                Create the first one
              </Link>
            </div>
          )}
        </article>
      </section>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  bordered = false,
}: {
  label: string;
  value: number;
  bordered?: boolean;
}) {
  return (
    <article
      className={`px-1 py-4 sm:px-5 ${
        bordered ? "border-base-300 border-b sm:border-r sm:border-b-0" : ""
      }`}
    >
      <p className="text-base-content/45 text-xs font-bold tracking-[0.16em] uppercase">
        {label}
      </p>
      <p className="mt-2 text-2xl font-bold tracking-tight">{value}</p>
    </article>
  );
}
