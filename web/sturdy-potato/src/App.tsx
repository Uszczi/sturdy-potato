import { useState } from "react";
import Login from "./pages/Login";
import LoggedOut from "./pages/LoggedOut";
import { isAuthenticated, logout } from "./services/auth";

type View = "login" | "app" | "loggedOut";

function App() {
  const [view, setView] = useState<View>(
    isAuthenticated() ? "app" : "login",
  );

  if (view === "login") {
    return <Login onSuccess={() => setView("app")} />;
  }

  if (view === "loggedOut") {
    return <LoggedOut onLogin={() => setView("login")} />;
  }

  function handleLogout() {
    logout();
    setView("loggedOut");
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

export default App;
