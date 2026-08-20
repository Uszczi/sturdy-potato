import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/logged-out")({
  component: LoggedOut,
});

function LoggedOut() {
  return (
    <main className="bg-base-200 grid min-h-screen place-items-center p-4">
      <div className="card bg-base-100 w-full max-w-sm shadow-xl">
        <div className="card-body items-center text-center">
          <h1 className="card-title text-2xl">Logged out</h1>
          <p className="text-base-content/70">
            You have been signed out of your account.
          </p>
          <div className="card-actions mt-2 w-full">
            <Link to="/login" className="btn btn-primary btn-block">
              Log in again
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
