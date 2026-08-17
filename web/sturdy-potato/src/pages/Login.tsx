import { useState } from "react";
import { ResponseError } from "../../api-client";
import { login } from "../services/auth";

type LoginProps = {
  onSuccess: () => void;
};

function Login({ onSuccess }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      onSuccess();
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
    <main className="grid min-h-screen place-items-center bg-base-200 p-4">
      <div className="card w-full max-w-sm bg-base-100 shadow-xl">
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
        </div>
      </div>
    </main>
  );
}

export default Login;
