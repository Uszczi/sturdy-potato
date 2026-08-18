import { useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import TaskListView from "../components/TaskListView";
import { useAppStore } from "../stores/app-store";

export const Route = createFileRoute("/_app/projects/$projectId")({
  component: ProjectDetail,
});

function ProjectDetail() {
  const { projectId } = Route.useParams();
  const id = Number(projectId);
  const loaded = useAppStore((state) => state.loaded);
  const project = useAppStore((state) =>
    state.projects.find((candidate) => candidate.id === id),
  );
  // Select the stable `tasks` array reference and derive the filtered list in
  // render. Filtering inside the selector would return a new array on every
  // call, which Zustand v5 (useSyncExternalStore) treats as a changed snapshot
  // and loops on ("getSnapshot should be cached").
  const allTasks = useAppStore((state) => state.tasks);
  const tasks = useMemo(
    () => allTasks.filter((task) => task.projectId === id),
    [allTasks, id],
  );

  if (!project) {
    return (
      <div className="container mx-auto max-w-5xl px-4 py-16 text-center">
        {loaded ? (
          <p className="text-base-content/60">This project no longer exists.</p>
        ) : (
          <span className="loading loading-spinner" aria-label="Loading" />
        )}
      </div>
    );
  }

  return (
    <TaskListView
      eyebrow="Project"
      heading={project.name}
      tasks={tasks}
      project={project}
    />
  );
}
