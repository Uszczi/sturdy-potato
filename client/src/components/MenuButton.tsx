import { useAppStore } from "../stores/app-store";

/** Hamburger that toggles the sidebar. Mirrors templates/_menu_button.html. */
function MenuButton() {
  const open = useAppStore((state) => state.sidebarOpen);
  const toggle = useAppStore((state) => state.toggleSidebar);
  return (
    <button
      type="button"
      className="btn -ml-2 btn-square shrink-0 btn-ghost"
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
