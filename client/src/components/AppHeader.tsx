import { useRef } from "react";
import MenuButton from "./MenuButton";
import { getUsername } from "../services/auth";
import { formatToday } from "../services/format";
import ThemeToggle from "./ThemeToggle";

/** Shared workspace header, including the control for the current sidebar. */
function AppHeader() {
  const username = getUsername();
  const workspaceModal = useRef<HTMLDialogElement>(null);

  return (
    <header className="border-base-300 flex flex-col gap-4 border-b pb-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="flex items-start gap-3">
        <MenuButton />
        <div>
          <p className="text-base-content/45 text-xs font-bold tracking-[0.18em] uppercase">
            {formatToday(new Date())}
          </p>
        </div>
      </div>
      <button
        type="button"
        onClick={() => workspaceModal.current?.showModal()}
        className="btn btn-ghost h-auto min-h-0 gap-3 px-2 py-1 sm:pt-1"
        aria-haspopup="dialog"
        aria-label="Open workspace settings"
      >
        <span className="hidden text-right sm:block">
          <span className="block text-sm font-bold">{username}</span>
          <span className="text-base-content/50 flex items-center justify-end gap-1 text-xs">
            Personal workspace
            <svg className="size-3" viewBox="0 0 16 16" aria-hidden="true">
              <path
                d="m4 6 4 4 4-4"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.5"
              />
            </svg>
          </span>
        </span>
        <span className="bg-primary text-primary-content grid size-9 place-items-center rounded-full text-sm font-bold">
          {username.charAt(0).toUpperCase()}
        </span>
      </button>

      <dialog ref={workspaceModal} className="modal">
        <div className="modal-box max-w-sm p-0">
          <div className="border-base-300 flex items-start justify-between border-b px-6 py-5">
            <div>
              <p className="text-base-content/50 text-xs font-bold tracking-[0.16em] uppercase">
                Workspace settings
              </p>
              <h2 className="mt-1 text-lg font-bold">Choose your theme</h2>
            </div>
            <form method="dialog">
              <button className="btn btn-circle btn-ghost btn-sm" aria-label="Close settings">
                <svg className="size-4" viewBox="0 0 16 16" aria-hidden="true">
                  <path d="m4 4 8 8M12 4l-8 8" stroke="currentColor" strokeLinecap="round" strokeWidth="1.5" />
                </svg>
              </button>
            </form>
          </div>
          <div className="px-4 py-4">
            <ThemeToggle embedded />
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button aria-label="Close settings">close</button>
        </form>
      </dialog>
    </header>
  );
}

export default AppHeader;
