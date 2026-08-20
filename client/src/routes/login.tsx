import { useState } from "react";
import {
  createFileRoute,
  Link,
  redirect,
  useNavigate,
} from "@tanstack/react-router";
import { ResponseError } from "@api-client";
import { login, loginAsDemo } from "@/services/auth";

type LoginSearch = {
  redirect?: string;
};

export const Route = createFileRoute("/login")({
  validateSearch: (search: Record<string, unknown>): LoginSearch => ({
    redirect: typeof search.redirect === "string" ? search.redirect : undefined,
  }),
  beforeLoad: ({ context, search }) => {
    if (context.isAuthenticated()) {
      throw redirect({ to: search.redirect ?? "/" });
    }
  },
  component: Login,
});

function Login() {
  const navigate = useNavigate();
  const search = Route.useSearch();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleDemoLogin() {
    setError(null);
    setSubmitting(true);
    try {
      await loginAsDemo();
      navigate({ to: search.redirect ?? "/" });
    } catch (err) {
      setError(
        err instanceof ResponseError && err.response.status === 401
          ? "Incorrect username or password."
          : "Something went wrong. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      navigate({ to: search.redirect ?? "/" });
    } catch (err) {
      setError(
        err instanceof ResponseError && err.response.status === 401
          ? "Incorrect username or password."
          : "Something went wrong. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="bg-base-200 grid min-h-screen place-items-center p-4">
      <div className="card bg-base-100 w-full max-w-sm shadow-xl">
        <div className="card-body">
          <h1 className="card-title text-2xl">Log in</h1>

          {error && (
            <div role="alert" className="alert alert-error alert-soft">
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <fieldset className="fieldset">
              <label className="label" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                className="input w-full"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />

              <label className="label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                className="input w-full"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />

              <button
                type="submit"
                className="btn btn-primary btn-block mt-4"
                disabled={submitting}
              >
                {submitting && <span className="loading loading-spinner" />}
                Log in
              </button>
            </fieldset>
          </form>

          <p className="text-center text-sm">or</p>

          <button
            onClick={handleDemoLogin}
            className="btn btn-secondary btn-block"
            disabled={submitting}
          >
            {submitting && <span className="loading loading-spinner" />}
            Log in using demo account
          </button>

          <p className="mt-2 text-center text-sm">
            Don't have an account?{" "}
            <Link to="/register" className="link link-primary">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
