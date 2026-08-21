import { createFileRoute, redirect } from "@tanstack/react-router";
import { DragDropProvider } from "@dnd-kit/react";
import type { TaskSchema } from "@api-client";
import { TaskStatus } from "@api-client";

import ProjectSelector from "@/components/kanban/ProjectSelector";
import Card from "@/components/kanban/Card";
import Column from "@/components/kanban/Column";
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
  const storeTasks = useAppStore((state) => state.tasks);
  const refresh = useAppStore((state) => state.refresh);
  const getTasksForProject = useAppStore((state) => state.getTasksForProject);
  const reorderTasks = useAppStore((state) => state.reorderTasks);
  const moveTask = useAppStore((state) => state.moveTask);
  const [tasks, setTasks] = useState<TaskSchema[]>([]);
  const [activeTaskId, setActiveTaskId] = useState<number | null>(null);
  const columnNames: TaskStatus[] = [TaskStatus.Open, TaskStatus.Done];

  const activeColumn =
    activeTaskId === null
      ? null
      : (tasks.find((task) => task.id === activeTaskId)?.status ?? null);

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    setTasks(getTasksForProject(selectedProject?.id ?? null));
  }, [selectedProject, storeTasks, getTasksForProject]);

  return (
    <main className="grid min-h-screen place-items-center p-4">
      <div className="flex h-full w-full flex-col">
        Kanban
        <ProjectSelector />
        <DragDropProvider
          onDragStart={(event) => {
            const { source } = event.operation;
            if (source?.type === "item") setActiveTaskId(source.id as number);
          }}
          onDragOver={(event) => {
            const { source, target } = event.operation;
            if (source?.type !== "item" || !target) return;

            setTasks((current) => {
              const moving = current.find((task) => task.id === source.id);
              if (!moving) return current;

              const targetColumn =
                target.type === "column"
                  ? (target.id as TaskStatus)
                  : current.find((task) => task.id === target.id)?.status;
              if (!targetColumn) return current;

              if (moving.status === targetColumn && target.id === source.id) {
                return current;
              }

              const without = current.filter((task) => task.id !== source.id);
              const moved = { ...moving, status: targetColumn };

              const targetIndex = without.findIndex(
                (task) => task.id === target.id,
              );
              if (targetIndex === -1) {
                let insertAt = without.length;
                for (let i = without.length - 1; i >= 0; i--) {
                  if (without[i].status === targetColumn) {
                    insertAt = i + 1;
                    break;
                  }
                  insertAt = i;
                }
                without.splice(insertAt, 0, moved);
              } else {
                without.splice(targetIndex, 0, moved);
              }
              return without;
            });
          }}
          onDragEnd={(event) => {
            const { source } = event.operation;
            setActiveTaskId(null);
            if (event.canceled) {
              setTasks(getTasksForProject(selectedProject?.id ?? null));
              return;
            }
            if (source?.type !== "item") return;

            const moved = tasks.find((task) => task.id === source.id);
            const original = storeTasks.find((task) => task.id === source.id);
            if (!moved || !original) return;

            const orderedIds = tasks
              .filter((task) => task.status === moved.status)
              .map((task) => task.id);
            if (moved.status !== original.status) {
              // Cross-column move: persist the new status and the destination
              // order together so the card holds the slot it was dropped into.
              moveTask(moved.id, moved.status, orderedIds);
            } else {
              // Same-column reorder: persist the new order of that column.
              reorderTasks(orderedIds);
            }
          }}
        >
          <div className="flex flex-1 flex-nowrap gap-4 overflow-x-auto">
            {columnNames.map((columnName) => (
              <Column
                key={columnName}
                id={columnName}
                name={columnName}
                highlighted={activeColumn === columnName}
              >
                {tasks
                  .filter((task) => task.status === columnName)
                  .map((task, index) => (
                    <Card
                      task={task}
                      id={task.id}
                      index={index}
                      key={task.id}
                      column={columnName}
                    />
                  ))}
              </Column>
            ))}
          </div>
        </DragDropProvider>
      </div>
    </main>
  );
}
