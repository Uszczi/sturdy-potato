import { useEffect, useRef, useState } from "react";
import { Link, createFileRoute } from "@tanstack/react-router";
import MenuButton from "../components/MenuButton";
import ProjectColorPicker from "../components/ProjectColorPicker";
import { useAppStore } from "../stores/app-store";
import type { ProjectSchema } from "../../api-client";

type ProjectsSearch = {
  compose?: boolean;
};

export const Route = createFileRoute("/_app/projects/")({
  validateSearch: (search: Record<string, unknown>): ProjectsSearch => ({
    compose: search.compose === true || search.compose === "1",
  }),
  component: Projects,
});

function Projects() {
  const { compose } = Route.useSearch();
  const projects = useAppStore((state) => state.projects);
  const reorderProjects = useAppStore((state) => state.reorderProjects);

  // Local copy so a drag reorders rows live; resyncs whenever the store hands
  // us a fresh list (after the reorder persists, or any other change).
  const [items, setItems] = useState(projects);
  const draggingId = useRef<number | null>(null);
  const [activeId, setActiveId] = useState<number | null>(null);

  useEffect(() => {
    setItems(projects);
  }, [projects]);

  function handleDragEnter(targetId: number) {
    const sourceId = draggingId.current;
    if (sourceId === null || sourceId === targetId) return;
    setItems((current) => {
      const from = current.findIndex((project) => project.id === sourceId);
      const to = current.findIndex((project) => project.id === targetId);
      if (from === -1 || to === -1) return current;
      const next = [...current];
      const [moved] = next.splice(from, 1);
      next.splice(to, 0, moved);
      return next;
    });
  }

  function handleDragEnd() {
    const dropped = draggingId.current !== null;
    draggingId.current = null;
    setActiveId(null);
    if (!dropped) return;
    const orderedIds = items.map((project) => project.id);
    const originalIds = projects.map((project) => project.id);
    if (orderedIds.some((id, index) => id !== originalIds[index])) {
      void reorderProjects(orderedIds);
    }
  }

  return (
    <div className="container mx-auto min-h-screen max-w-5xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <header className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <MenuButton />
          <div>
            <p className="text-xs font-bold tracking-[0.18em] text-base-content/45 uppercase">
              Workspace
            </p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
              Projects
            </h1>
          </div>
        </div>
        <Link
          to="/tasks"
          className="btn gap-2 self-start btn-ghost text-base-content/60 btn-sm hover:bg-base-200 hover:text-base-content"
        >
          Inbox
          <svg
            aria-hidden="true"
            className="size-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="1.8"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m15 19-7-7 7-7" />
          </svg>
        </Link>
      </header>

      <ProjectComposer composeDefault={compose} />

      <section id="project-section" aria-labelledby="project-list-heading">
        <h2 id="project-list-heading" className="sr-only">
          Your projects
        </h2>
        {projects.length > 0 ? (
          <ul
            className="divide-y divide-base-300 border-y border-base-300"
            aria-label="Project list"
          >
            {items.map((project) => (
              <li
                key={project.id}
                draggable
                onDragStart={() => {
                  draggingId.current = project.id;
                  setActiveId(project.id);
                }}
                onDragEnter={() => handleDragEnter(project.id)}
                onDragOver={(event) => event.preventDefault()}
                onDragEnd={handleDragEnd}
                className={activeId === project.id ? "opacity-50" : ""}
              >
                <div className="group flex items-center gap-1 transition-colors hover:bg-base-200">
                  <span
                    className="drag-handle ml-1 grid size-8 shrink-0 cursor-grab place-items-center rounded-md text-base-content/30 active:cursor-grabbing sm:ml-2"
                    aria-hidden="true"
                  >
                    <svg
                      className="size-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                    >
                      <path d="M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01" />
                    </svg>
                  </span>
                  <ProjectRowColor project={project} />
                  <Link
                    to="/projects/$projectId"
                    params={{ projectId: String(project.id) }}
                    className="flex min-w-0 flex-1 items-center gap-3 px-2 py-3.5 transition-colors focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-primary sm:px-3"
                  >
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-semibold">
                        {project.name}
                      </span>
                      <span className="mt-0.5 block text-xs text-base-content/50">
                        {project.taskCount ?? 0}{" "}
                        {(project.taskCount ?? 0) === 1 ? "task" : "tasks"}
                      </span>
                    </span>
                    <svg
                      aria-hidden="true"
                      className="size-4 shrink-0 text-base-content/35"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m9 5 7 7-7 7"
                      />
                    </svg>
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="border-y border-base-300 px-4 py-12 text-center sm:py-16">
            <span className="mx-auto grid size-10 place-items-center rounded-full bg-base-200 text-primary">
              <svg
                aria-hidden="true"
                className="size-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 7h16M4 12h16M4 17h10"
                />
              </svg>
            </span>
            <h2 className="mt-3 text-lg font-semibold">No projects yet.</h2>
            <p className="mx-auto max-w-sm text-sm leading-6 text-base-content/65">
              Add a project above, then give related tasks a home.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

/** The collapsible "Add project" form. */
function ProjectRowColor({ project }: { project: ProjectSchema }) {
  const updateProject = useAppStore((state) => state.updateProject);
  return (
    <span className="shrink-0">
      <ProjectColorPicker
        value={project.color}
        label={project.name}
        onSelect={(color) => void updateProject(project.id, { color })}
      />
    </span>
  );
}

function ProjectComposer({ composeDefault }: { composeDefault?: boolean }) {
  const addProject = useAppStore((state) => state.addProject);
  const [open, setOpen] = useState(Boolean(composeDefault));
  const [name, setName] = useState("");
  const [color, setColor] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);

  function reveal() {
    setOpen(true);
    requestAnimationFrame(() => nameRef.current?.focus());
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    await addProject(name, color);
    setSubmitting(false);
    setName("");
    setColor(null);
  }

  return (
    <section className="mb-6" aria-label="Add a project">
      {!open && (
        <button
          type="button"
          aria-expanded={open}
          aria-controls="project-composer"
          onClick={reveal}
          className="group flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left text-sm text-base-content/55 transition hover:bg-base-200 hover:text-primary"
        >
          <span className="grid size-6 place-items-center rounded-full text-primary transition group-hover:bg-primary group-hover:text-primary-content">
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
          </span>
          <span className="font-semibold">Add project</span>
        </button>
      )}
      {open && (
        <form
          id="project-composer"
          onSubmit={handleSubmit}
          className="overflow-hidden rounded-lg border border-base-300 bg-base-100 shadow-sm"
        >
          <label className="sr-only" htmlFor="project-name">
            New project name
          </label>
          <input
            id="project-name"
            ref={nameRef}
            name="name"
            type="text"
            className="input w-full input-ghost px-4 py-3 text-base font-medium focus:outline-none"
            placeholder="What is this project about?"
            maxLength={100}
            autoComplete="off"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
          <div className="flex items-center gap-2 border-t border-base-300 px-3 py-2">
            <ProjectColorPicker
              value={color}
              label="new project"
              onSelect={setColor}
            />
            <button
              type="button"
              className="btn ml-auto btn-ghost btn-sm"
              onClick={() => {
                setName("");
                setColor(null);
                setOpen(false);
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={submitting}
            >
              Add project
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
