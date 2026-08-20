import { createFileRoute, redirect } from "@tanstack/react-router";

import ProjectSelector from "@/components/kanban/ProjectSelector";
import Card from "@/components/kanban/Card";
import { useAppStore } from "@/stores/app-store";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/kanban/")({
  beforeLoad: ({ context, location }) => {
    if (!context.isAuthenticated()) {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }
  },
  component: Kanban,
});

function Kanban() {
  const selectedProject = useAppStore((state) => state.kanbanSelectedProject);
  const projects = useAppStore((state) => state.projects);
  const refresh = useAppStore((state) => state.refresh);
  const getTasksForProject = useAppStore((state) => state.getTasksForProject);
  const [tasks, setTasks] = useState([]);
  const columnNames = ["TODO", "DOING", "DONE"];

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    setTasks(getTasksForProject(selectedProject?.id));
  }, [selectedProject]);

  return (
    <main className="bg-base-200 grid min-h-screen place-items-center p-4">
      <div className="card bg-base-100 h-full w-full shadow-xl">
        Kanban
        <ProjectSelector />
        <div className="grid grid-cols-3 gap-4">
          {columnNames.map((columnName) => (
            <div key={columnName} className="flex flex-col gap-4">
              <h1>{columnName}</h1>

              {tasks.map((task) => (
                <Card task={task} />
              ))}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
