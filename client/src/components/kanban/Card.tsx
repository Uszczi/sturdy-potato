import type { TaskSchema } from "@api-client";
import React from "react";
import { useSortable } from "@dnd-kit/react/sortable";

export default function Card({
  id,
  index,
  column,
  task,
}: {
  id: number;
  index: number;
  column: string;
  task: TaskSchema;
}) {
  const { ref, isDragging } = useSortable({
    id,
    index,
    type: "item",
    accept: "item",
    group: column,
  });

  return (
    <div
      className="card bg-base-100 w-56 shadow-sm"
      ref={ref}
      data-dragging={isDragging}
      data-testid={`card-${id}`}
    >
      <div className="card-body">
        <h2 className="text-2xl font-bold">{task.title}</h2>
        {task.description.trim().length > 0 && (
          <p className="text-sm opacity-50">{task.description.slice(0, 100)}</p>
        )}
      </div>
    </div>
  );
}
