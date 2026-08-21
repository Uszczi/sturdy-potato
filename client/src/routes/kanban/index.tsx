import { createFileRoute, redirect } from "@tanstack/react-router";
import { DragDropProvider } from "@dnd-kit/react";
import type { TaskSchema } from "@api-client";
import { TaskStatus } from "@api-client";

import AppLayout from "@/components/AppLayout";
import Card from "@/components/kanban/Card";
import Column from "@/components/kanban/Column";
import { KanbanSidebar } from "@/components/kanban/KanbanSidebar";
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
  const projectId = selectedProject?.id ?? null;
  const ensureBoard = useAppStore((state) => state.ensureBoard);
  const storeTasks = useAppStore((state) => state.getBoard(projectId));
  const moveTask = useAppStore((state) => state.moveTask);
  const [tasks, setTasks] = useState<TaskSchema[]>([]);
  const [activeTaskId, setActiveTaskId] = useState<number | null>(null);
  const columnNames: TaskStatus[] = [TaskStatus.Open, TaskStatus.Done];

  const activeColumn =
    activeTaskId === null
      ? null
      : (tasks.find((task) => task.id === activeTaskId)?.status ?? null);

  // Load only the selected board's tasks, the first time it's opened.
  useEffect(() => {
    void ensureBoard(projectId);
  }, [projectId, ensureBoard]);

  useEffect(() => {
    setTasks(storeTasks);
  }, [storeTasks]);

  return (
    <AppLayout sidebar={<KanbanSidebar />}>
      <div className="flex min-h-screen flex-col p-4 sm:p-6">
        <div className="flex h-full w-full flex-col">
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
                setTasks(storeTasks);
                return;
              }
              if (source?.type !== "item") return;

              const moved = tasks.find((task) => task.id === source.id);
              const original = storeTasks.find((task) => task.id === source.id);
              if (!moved || !original) return;

              // Where the card ended up within its (possibly new) column. A move
              // that changed neither status nor slot is a no-op we can skip.
              const column = tasks.filter(
                (task) => task.status === moved.status,
              );
              const position = column.findIndex((task) => task.id === moved.id);
              const originalColumn = storeTasks.filter(
                (task) => task.status === moved.status,
              );
              const originalPosition = originalColumn.findIndex(
                (task) => task.id === moved.id,
              );
              if (
                moved.status === original.status &&
                position === originalPosition
              ) {
                return;
              }
              // One call carries the destination status and slot together.
              moveTask(moved.id, moved.status, position);
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
      </div>
    </AppLayout>
  );
}
