import { createFileRoute } from "@tanstack/react-router";
import TaskListView from "../components/TaskListView";
import { useAppStore } from "../stores/app-store";
import { dayKey, todayKey } from "../services/format";

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
  const tasks = useAppStore((state) => state.tasks);

  const today = todayKey();
  const visible = tasks.filter((task) => {
    if (!view) return true; // Inbox shows everything.
    if (!task.dueDate) return false;
    const key = dayKey(task.dueDate);
    return view === "today" ? key === today : key > today;
  });

  return (
    <TaskListView
      eyebrow="Tasks"
      heading={view ? HEADINGS[view] : "Inbox"}
      tasks={visible}
      composeDefault={compose}
    />
  );
}
