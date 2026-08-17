import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { isAuthenticated, logout } from "../services/auth";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  return isAuthenticated() ? <SignedIn /> : <Landing />;
}

function SignedIn() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate({ to: "/logged-out" });
  }

  return (
    <main className="grid min-h-screen place-items-center bg-base-200 p-4">
      <div className="card w-full max-w-sm bg-base-100 shadow-xl">
        <div className="card-body items-center text-center">
          <h1 className="card-title text-2xl">You're signed in</h1>
          <p className="text-base-content/70">Welcome to sturdy potato.</p>
          <div className="card-actions mt-2 w-full">
            <button
              type="button"
              className="btn btn-block"
              onClick={handleLogout}
            >
              Log out
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

function Landing() {
  return (
    <main className="grid min-h-screen place-items-center bg-base-200 p-4">
      <div className="card w-full max-w-sm bg-base-100 shadow-xl">
        <div className="card-body items-center text-center">
          <h1 className="card-title text-2xl">Welcome to sturdy potato</h1>
          <p className="text-base-content/70">Log in to access your account.</p>
          <div className="card-actions mt-2 w-full">
            <Link to="/login" className="btn btn-primary btn-block">
              Log in
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
