type LoggedOutProps = {
  onLogin: () => void;
};

function LoggedOut({ onLogin }: LoggedOutProps) {
  return (
    <main className="grid min-h-screen place-items-center bg-base-200 p-4">
      <div className="card w-full max-w-sm bg-base-100 shadow-xl">
        <div className="card-body items-center text-center">
          <h1 className="card-title text-2xl">Logged out</h1>
          <p className="text-base-content/70">
            You have been signed out of your account.
          </p>
          <div className="card-actions mt-2 w-full">
            <button
              type="button"
              className="btn btn-primary btn-block"
              onClick={onLogin}
            >
              Log in again
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

export default LoggedOut;
