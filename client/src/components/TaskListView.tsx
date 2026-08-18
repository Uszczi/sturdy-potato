import { useEffect, useRef, useState } from "react";
import type { ProjectSchema, TodoSchema } from "../../api-client";
import { Link } from "@tanstack/react-router";
import { useAppStore } from "../stores/app-store";
import {
  formatDueLong,
  formatDueShort,
  formatTimestamp,
} from "../services/format";
import MenuButton from "./MenuButton";

type TaskListViewProps = {
  /** Small uppercase label above the heading ("Tasks" or "Project"). */
  eyebrow: string;
  heading: string;
  /** Tasks already filtered for this view. */
  tasks: TodoSchema[];
  /** Present on the project detail page; drives the dot, count and empty copy. */
  project?: ProjectSchema;
  /** Open the composer on first render (the `?compose=1` entry point). */
  composeDefault?: boolean;
};

/**
 * The task list page shell: header, add-task composer, the task list and a
 * detail modal. Mirrors templates/todo/task_list.html and its partials.
 */
function TaskListView({
  eyebrow,
  heading,
  tasks,
  project,
  composeDefault = false,
}: TaskListViewProps) {
  const [selected, setSelected] = useState<TodoSchema | null>(null);

  return (
    <div className="container mx-auto min-h-screen max-w-5xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <header className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <MenuButton />
          {project && (
            <span
              className="mt-2 size-3 shrink-0 rounded-full bg-primary"
              aria-hidden="true"
            />
          )}
          <div>
            <p className="text-xs font-bold tracking-[0.18em] text-base-content/45 uppercase">
              {eyebrow}
            </p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
              {heading}
            </h1>
            {project && (
              <p className="mt-2 text-sm text-base-content/55">
                {project.taskCount ?? 0}{" "}
                {(project.taskCount ?? 0) === 1 ? "task" : "tasks"}
              </p>
            )}
          </div>
        </div>
        <Link
          to="/projects"
          className="btn gap-2 self-start btn-ghost text-base-content/60 btn-sm hover:bg-base-200 hover:text-base-content"
        >
          {project ? "All projects" : "Projects"}
          <svg
            aria-hidden="true"
            className="size-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="1.8"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m9 5 7 7-7 7" />
          </svg>
        </Link>
      </header>

      <TaskComposer defaultProjectId={project?.id} composeDefault={composeDefault} />

      <section aria-labelledby="task-list-heading">
        <h2 id="task-list-heading" className="sr-only">
          Your tasks
        </h2>
        <div id="task-section">
          {tasks.length > 0 ? (
            <ul
              id="task-list"
              className="divide-y divide-base-300 border-y border-base-300"
              aria-label="Task list"
            >
              {tasks.map((task) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  onOpen={() => setSelected(task)}
                />
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
                  strokeWidth="2"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="m5 12 4 4L19 6"
                  />
                </svg>
              </span>
              <h2 className="mt-3 text-lg font-semibold">
                {project ? "No tasks in this project yet." : "No tasks yet."}
              </h2>
              <p className="mx-auto max-w-sm text-sm leading-6 text-base-content/65">
                {project
                  ? "Add a task above to start this project moving."
                  : "Your inbox is quiet. New tasks will appear here when you add them."}
              </p>
            </div>
          )}
        </div>
      </section>

      <TaskModal task={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

/** The collapsible "Add task" form. */
function TaskComposer({
  defaultProjectId,
  composeDefault,
}: {
  defaultProjectId?: number;
  composeDefault: boolean;
}) {
  const projects = useAppStore((state) => state.projects);
  const addTask = useAppStore((state) => state.addTask);
  const [open, setOpen] = useState(composeDefault);
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [projectId, setProjectId] = useState(
    defaultProjectId ? String(defaultProjectId) : "",
  );
  const [submitting, setSubmitting] = useState(false);
  const titleRef = useRef<HTMLInputElement>(null);

  function reveal() {
    setOpen(true);
    // Focus the title once the field is visible.
    requestAnimationFrame(() => titleRef.current?.focus());
  }

  function reset() {
    setTitle("");
    setDueDate("");
    setProjectId(defaultProjectId ? String(defaultProjectId) : "");
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    await addTask({
      title,
      dueDate: dueDate ? new Date(dueDate) : null,
      projectId: projectId ? Number(projectId) : null,
    });
    setSubmitting(false);
    reset();
  }

  return (
    <section className="mb-6" aria-label="Add a task">
      {!open && (
        <button
          type="button"
          aria-expanded={open}
          aria-controls="task-composer"
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
          <span className="font-semibold">Add task</span>
        </button>
      )}
      {open && (
        <form
          id="task-composer"
          onSubmit={handleSubmit}
          className="overflow-hidden rounded-lg border border-base-300 bg-base-100 shadow-sm"
        >
          <label className="sr-only" htmlFor="task-title">
            New task title
          </label>
          <input
            id="task-title"
            ref={titleRef}
            name="title"
            type="text"
            className="input w-full input-ghost px-4 pt-3 text-base font-medium focus:outline-none"
            placeholder="What needs to be done?"
            maxLength={200}
            autoComplete="off"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
          />
          <div className="flex flex-wrap items-center gap-2 border-t border-base-300 px-3 py-2">
            <label className="sr-only" htmlFor="task-due-date">
              Due date
            </label>
            <input
              id="task-due-date"
              name="due_date"
              type="date"
              className="input-bordered input w-auto input-sm"
              aria-label="Due date"
              value={dueDate}
              onChange={(event) => setDueDate(event.target.value)}
            />
            <label className="sr-only" htmlFor="task-project">
              Project
            </label>
            <select
              id="task-project"
              name="project_id"
              className="select-bordered select max-w-48 select-sm"
              aria-label="Project"
              value={projectId}
              onChange={(event) => setProjectId(event.target.value)}
            >
              <option value="">No project</option>
              {projects.map((available) => (
                <option key={available.id} value={String(available.id)}>
                  {available.name}
                </option>
              ))}
            </select>
            <div className="ml-auto flex items-center gap-2">
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  reset();
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
                Add task
              </button>
            </div>
          </div>
        </form>
      )}
    </section>
  );
}

/** A single task row with completion toggle and inline project assignment. */
function TaskRow({ task, onOpen }: { task: TodoSchema; onOpen: () => void }) {
  const projects = useAppStore((state) => state.projects);
  const toggleTask = useAppStore((state) => state.toggleTask);
  const assignTaskProject = useAppStore((state) => state.assignTaskProject);

  function activate(event: React.KeyboardEvent) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onOpen();
    }
  }

  return (
    <li
      id={`task-${task.id}`}
      className="group cursor-pointer transition-colors duration-200 hover:bg-base-200/60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
      role="button"
      tabIndex={0}
      onClick={onOpen}
      onKeyDown={activate}
    >
      <div className="flex items-start gap-3 px-3 py-3 sm:px-4">
        <span
          className="drag-handle mt-0.5 grid size-5 shrink-0 place-items-center rounded text-base-content/25"
          aria-hidden="true"
        >
          <svg
            className="size-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
          >
            <path d="M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01" />
          </svg>
        </span>
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            void toggleTask(task);
          }}
          className={`${
            task.completed
              ? "border-success bg-success text-success-content"
              : "border-base-content/30 text-transparent hover:border-primary hover:text-primary"
          } mt-0.5 grid size-5 shrink-0 place-items-center rounded-full border-2 transition-colors`}
          aria-pressed={task.completed}
          aria-label={
            task.completed
              ? `Mark ${task.title} as open`
              : `Mark ${task.title} as complete`
          }
        >
          <svg
            aria-hidden="true"
            className="size-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m5 12 4 4L19 6" />
          </svg>
        </button>
        <div className="min-w-0 flex-1">
          <h2
            className={`${
              task.completed ? "text-base-content/45 line-through" : ""
            } text-sm font-medium break-words`}
          >
            {task.title}
          </h2>
          {task.dueDate && (
            <div className="mt-1 flex items-center gap-2 text-xs text-base-content/50">
              <svg
                aria-hidden="true"
                className="size-3.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <rect width="16" height="16" x="4" y="5" rx="2" />
                <path strokeLinecap="round" d="M8 3v4m8-4v4M4 10h16" />
              </svg>
              <span>{formatDueShort(task.dueDate)}</span>
            </div>
          )}
        </div>
        <select
          id={`task-project-${task.id}`}
          name="project_id"
          className="select max-w-32 select-ghost text-xs font-medium text-base-content/50 opacity-70 transition select-xs group-hover:opacity-100 focus:opacity-100"
          aria-label={`Project for ${task.title}`}
          value={task.projectId ? String(task.projectId) : ""}
          onClick={(event) => event.stopPropagation()}
          onChange={(event) => {
            event.stopPropagation();
            const value = event.target.value;
            void assignTaskProject(task.id, value ? Number(value) : null);
          }}
        >
          <option value="">No project</option>
          {projects.map((project) => (
            <option key={project.id} value={String(project.id)}>
              {project.name}
            </option>
          ))}
        </select>
      </div>
    </li>
  );
}

/** Read-only task detail dialog. Mirrors the modal in todo/task_list.html. */
function TaskModal({
  task,
  onClose,
}: {
  task: TodoSchema | null;
  onClose: () => void;
}) {
  const projects = useAppStore((state) => state.projects);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!task) return;
    closeRef.current?.focus();
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [task, onClose]);

  if (!task) return null;

  const projectName =
    projects.find((project) => project.id === task.projectId)?.name ??
    "No project";

  return (
    <div
      className="modal modal-open"
      role="dialog"
      aria-modal="true"
      aria-labelledby="task-modal-title"
      onClick={onClose}
    >
      <article
        className="modal-box max-w-lg"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold tracking-[0.2em] text-primary uppercase">
              Task details
            </p>
            <h2 id="task-modal-title" className="mt-2 text-2xl font-bold">
              {task.title}
            </h2>
          </div>
          <button
            type="button"
            ref={closeRef}
            className="btn btn-circle btn-ghost btn-sm"
            aria-label="Close task details"
            onClick={onClose}
          >
            <svg
              aria-hidden="true"
              className="size-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path strokeLinecap="round" d="m6 6 12 12M18 6 6 18" />
            </svg>
            <span className="sr-only">Close</span>
          </button>
        </header>
        {task.description && (
          <p className="mt-6 whitespace-pre-line text-base-content/75">
            {task.description}
          </p>
        )}
        <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-base-300 pt-5 text-sm">
          <Detail label="Status">
            <span className="badge badge-outline">
              {task.completed ? "Completed" : "Open"}
            </span>
          </Detail>
          <Detail label="Project">{projectName}</Detail>
          <Detail label="Due">
            {task.dueDate ? formatDueLong(task.dueDate) : "No due date"}
          </Detail>
          <Detail label="Created">{formatTimestamp(task.createdAt)}</Detail>
          <Detail label="Updated">{formatTimestamp(task.updatedAt)}</Detail>
        </dl>
      </article>
    </div>
  );
}

function Detail({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <dt className="text-xs font-bold tracking-wider text-base-content/50 uppercase">
        {label}
      </dt>
      <dd className="mt-2 text-base-content/75">{children}</dd>
    </div>
  );
}

export default TaskListView;
