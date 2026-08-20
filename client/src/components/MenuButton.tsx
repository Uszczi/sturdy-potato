import { useAppStore } from "../stores/app-store";

/** Hamburger that toggles the sidebar. Mirrors templates/_menu_button.html. */
function MenuButton() {
  const open = useAppStore((state) => state.sidebarOpen);
  const toggle = useAppStore((state) => state.toggleSidebar);
  return (
    <button
      type="button"
      className="btn btn-square btn-ghost -ml-2 shrink-0"
      onClick={toggle}
      aria-label={open ? "Close navigation" : "Open navigation"}
    >
      <span aria-hidden="true" className="text-xl">
        ☰
      </span>
    </button>
  );
}

export default MenuButton;
