import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import type { TaskSchema } from "@api-client";
import TaskListView from "../components/TaskListView";
import { useAppStore } from "../stores/app-store";
import { fetchDateView } from "../services/tasks";

type TaskView = "today" | "upcoming";

type TasksSearch = {
  view?: TaskView;
  compose?: boolean;
};

export const Route = createFileRoute("/_app/tasks")({
  validateSearch: (search: Record<string, unknown>): TasksSearch => ({
    view:
      search.view === "today" || search.view === "upcoming"
        ? search.view
        : undefined,
    // Only carry `compose` when it's on, so plain navigations (e.g. the Inbox
    // link) keep a clean `/tasks` URL instead of `?compose=false`.
    compose: search.compose === true || search.compose === "1" || undefined,
  }),
  component: Tasks,
});

const HEADINGS: Record<TaskView, string> = {
  today: "Today",
  upcoming: "Upcoming",
};

function Tasks() {
  const { view, compose } = Route.useSearch();
  return view ? (
    <DateView view={view} />
  ) : (
    <Inbox composeDefault={compose} />
  );
}

/** The inbox is the null-project board: its own column, drag-reorderable. */
function Inbox({ composeDefault }: { composeDefault?: boolean }) {
  const ensureBoard = useAppStore((state) => state.ensureBoard);
  const tasks = useAppStore((state) => state.getBoard(null));

  useEffect(() => {
    void ensureBoard(null);
  }, [ensureBoard]);

  return (
    <TaskListView
      eyebrow="Tasks"
      heading="Inbox"
      tasks={tasks}
      composeDefault={composeDefault}
      reorderable
    />
  );
}

/**
 * Today/upcoming span every board, so they're fetched on their own (ordered by
 * due date + recency on the server) and are read-only — no drag reordering.
 */
function DateView({ view }: { view: TaskView }) {
  const [tasks, setTasks] = useState<TaskSchema[]>([]);

  useEffect(() => {
    let active = true;
    void fetchDateView(view).then((result) => {
      if (active) setTasks(result);
    });
    return () => {
      active = false;
    };
  }, [view]);

  return (
    <TaskListView eyebrow="Tasks" heading={HEADINGS[view]} tasks={tasks} />
  );
}
