import {
  createFileRoute,
  redirect,
} from "@tanstack/react-router";


export const Route = createFileRoute("/kanban/")({
  beforeLoad: ({ context, location }) => {
    if (!context.isAuthenticated()) {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }
  },
  component: Kanban
});

function Kanban() {
  return (
    <main className="grid min-h-screen place-items-center bg-base-200 p-4">
      <div className="card w-full max-w-sm bg-base-100 shadow-xl">
      Kanban
      </div>
    </main>
  );
}
