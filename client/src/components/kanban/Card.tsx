import type { TaskSchema } from "@api-client";

export default function Card({ task }: { task: TaskSchema }) {
  return (
    <div className="card bg-base-100 w-96 shadow-sm">
      <div className="card-body">
        <h2 className="text-3xl font-bold">{task.title}</h2>
        {task.description.trim().length > 0 && (
          <p className="text-sm opacity-50">{task.description.slice(0, 100)}</p>
        )}
      </div>
    </div>
  );
}
